#!/usr/bin/env python3
"""Unit tests for the parallel SCJ queue (lock, id reservation, monotonic next_seq)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scj_lock
import scj_queue


class DirLockTests(unittest.TestCase):
    def test_two_threads_serialize(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "lock")
            counter = {"n": 0}

            def work():
                for _ in range(40):
                    with scj_lock.DirLock(path, timeout=10):
                        cur = counter["n"]
                        time.sleep(0.001)
                        counter["n"] = cur + 1

            t1 = threading.Thread(target=work)
            t2 = threading.Thread(target=work)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.assertEqual(counter["n"], 80)

    def test_stale_lock_stolen_when_pid_dead(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "lock")
            os.mkdir(path)
            with open(os.path.join(path, "pid"), "w", encoding="utf-8") as f:
                f.write("99999999")
            with scj_lock.DirLock(path, timeout=5) as lock:
                self.assertTrue(lock.held)
            self.assertFalse(os.path.isdir(path))


class QueueTests(unittest.TestCase):
    def test_next_free_seq_skips_open_tickets(self):
        state = {"next_seq": 10, "cases": [{"case_id": "SCJ-009", "status": "done"}]}
        tickets = [
            {"case_id": "SCJ-010", "status": "READY", "source": "a.pdf"},
            {"case_id": "SCJ-011", "status": "AUTHORING", "source": "b.pdf"},
        ]
        self.assertEqual(scj_queue.next_free_seq(state, tickets), 12)

    def test_two_claims_get_distinct_ids(self):
        state = {"next_seq": 537, "cases": [{"case_id": "SCJ-536", "status": "done"}]}
        tickets = []
        seen = []
        for _ in range(3):
            seq = scj_queue.next_free_seq(state, tickets)
            cid = scj_queue.case_id_for(seq)
            self.assertNotIn(seq, seen)
            seen.append(seq)
            tickets.append({"case_id": cid, "status": "READY", "source": f"{seq}.pdf"})
            scj_queue.bump_next_seq(state, seq)
        self.assertEqual(seen, [537, 538, 539])
        self.assertEqual(state["next_seq"], 540)

    def test_finalize_does_not_rewind_reservations(self):
        state = {
            "next_seq": 540,
            "cases": [
                {"case_id": "SCJ-536", "status": "done"},
                {"case_id": "SCJ-537", "status": "done"},
            ],
        }
        # 538 and 539 are inflight; 537 just finalized
        self.assertEqual(scj_queue.next_seq_after_finalize(state), 540)

    def test_finalize_bumps_when_no_reservation(self):
        state = {
            "next_seq": 537,
            "cases": [{"case_id": "SCJ-537", "status": "done"}],
        }
        self.assertEqual(scj_queue.next_seq_after_finalize(state), 538)

    def test_open_sources_and_save_ticket(self):
        with tempfile.TemporaryDirectory() as td:
            tdir = os.path.join(td, "tickets")
            legacy = os.path.join(td, "NEXT_TICKET.json")
            ticket = {
                "status": "READY",
                "case_id": "SCJ-537",
                "source": "2025/foo.pdf",
                "authoring": "short",
            }
            dest = scj_queue.save_ticket(
                ticket, tickets_dir=tdir, legacy_path=legacy
            )
            self.assertTrue(os.path.exists(dest))
            self.assertTrue(os.path.exists(legacy))
            srcs = scj_queue.open_sources(tdir)
            self.assertIn("2025/foo.pdf", srcs)
            self.assertIn("foo.pdf", srcs)

    def test_json_only_prompt_rewrites_ticket_path(self):
        base = "Read supply-code/tmp/NEXT_TICKET.json first.\nThen finalize.\n"
        out = scj_queue.make_json_only_prompt(
            base,
            "supply-code/tmp/tickets/SCJ-537.json",
            "SCJ-537",
            "supply-code/summaries/json/SCJ-537.json",
        )
        self.assertIn("supply-code/tmp/tickets/SCJ-537.json", out)
        self.assertNotIn("supply-code/tmp/NEXT_TICKET.json", out)
        self.assertIn("Do NOT run finalize_scj.py", out)

    def test_ticket_takeable_ready_and_dead_owner(self):
        self.assertTrue(scj_queue.ticket_takeable({"status": "READY"}))
        self.assertTrue(scj_queue.ticket_takeable({
            "status": "AUTHORING", "owner_pid": 99999999,
        }))
        self.assertFalse(scj_queue.ticket_takeable({
            "status": "AUTHORING", "owner_pid": os.getpid(),
        }))
        self.assertFalse(scj_queue.ticket_takeable({"status": "CLAIMING"}))

    def test_atomic_write_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.json")
            scj_queue.atomic_write_json(p, {"a": 1})
            with open(p, encoding="utf-8") as f:
                self.assertEqual(json.load(f)["a"], 1)


class PriorityQueueTests(unittest.TestCase):
    def test_sort_puts_priority_before_year_folders(self):
        import prepare_next_scj as p
        files = [
            "2007/a.pdf",
            "priority/2015/z.pdf",
            "2024/b.pdf",
            "priority/2009/a.pdf",
        ]
        files.sort(key=p.queue_sort_key)
        self.assertEqual(
            files,
            [
                "priority/2009/a.pdf",
                "priority/2015/z.pdf",
                "2007/a.pdf",
                "2024/b.pdf",
            ],
        )

    def test_is_priority_source(self):
        import prepare_next_scj as p
        self.assertTrue(p.is_priority_source("priority/2009/x.pdf"))
        self.assertTrue(p.is_priority_source("priority"))
        self.assertFalse(p.is_priority_source("2009/x.pdf"))
        self.assertFalse(p.is_priority_source("2009/priority.pdf"))
        self.assertFalse(p.is_priority_source("priority-hold/x.pdf"))

    def test_priority_source_forces_full_even_when_short(self):
        import prepare_next_scj as p
        ticket = {
            "source": "priority/2009/WRIC(A)_1_2009.pdf",
            "word_count": 400,
            "page_count": 2,
            "citation_count": 0,
        }
        p.apply_llm_authoring(ticket, "short order text", {"citation_count": 0})
        self.assertEqual(ticket["authoring"], "full")
        self.assertEqual(ticket["gate"], "priority-full")
        self.assertEqual(ticket["prompt"], "tools/prompts/next_case_once.txt")

    def test_non_priority_still_goes_short(self):
        import prepare_next_scj as p
        ticket = {
            "source": "2022/WRIC(A)_1_2022.pdf",
            "word_count": 400,
            "page_count": 2,
            "citation_count": 0,
        }
        p.apply_llm_authoring(ticket, "short order text", {"citation_count": 0})
        self.assertEqual(ticket["authoring"], "short")


if __name__ == "__main__":
    unittest.main()
