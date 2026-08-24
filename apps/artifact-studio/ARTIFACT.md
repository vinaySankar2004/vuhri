---
type: Learning Artifact Brief
title: Artifact Studio component preview
status: built
format: interactive-web
---

# Learning objective

Predict how three-state depth-first search changes as a small directed graph is traversed, then explain why an edge to a completed node does not by itself form a cycle.

# Demonstrated need

This preview tests the first shared artifact primitives and verification workflow. It is not based on learner performance evidence yet.

# Learning action

The learner steps through visible graph states, predicts whether a shown edge forms a cycle, receives misconception-specific feedback, and can reset the whole activity.

# Direction

Use five states: enter A, enter B, complete B, enter C, and complete the search. Keep active, complete, and unvisited states visible. Present the prediction separately so the learner can answer at any point. An incorrect answer should distinguish "seen before" from "active on the current path."

# Success evidence

Outside the interface, ask the learner to explain why an edge to a completed node is safe and what kind of edge would prove a cycle. The preview must not be described as instructionally effective until this check is observed.

# Sources and assumptions

The graph and wording are a deliberately small demonstration of the three-state DFS cycle-detection model. A learner-facing artifact must replace the preview labels with authoritative sources and declare any further simplifications.
