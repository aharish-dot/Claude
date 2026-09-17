"""scjlib — deterministic helpers for the SCJ summarization pipeline.

Nothing in here calls an LLM or the network. The legal authoring step is done by
Claude inside the chat session (see prompts/authoring_card.md); these modules only
prepare inputs and check outputs so that authoring stays cheap enough to do >=20
cases in a single session.
"""
