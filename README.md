# Converted OS

> An experimental AI-native operating system prototype built on Linux, focused on autonomous computer control, adaptive planning, learning, and safe tool execution.

## Overview

**Converted OS** is an experimental operating system concept built around the idea that computers should understand **goals**, rather than requiring users to manually specify every individual action.

The project uses Linux as its foundation and adds an AI orchestration layer capable of:

- Understanding a user's high-level goal
- Creating a temporary workflow
- Planning tool-based actions
- Executing actions through controlled tools
- Observing execution results
- Recovering from failures
- Learning from previous experiences
- Improving future planning using learned experiences
- Applying risk and permission policies before sensitive actions

The long-term goal is to create an AI-native operating system where the AI acts as an autonomous computer operator while remaining constrained by controlled tools, policies, and permissions.

---

## Project Status

**Current stage: Experimental prototype**

The core task-management, planning, tool-execution, recovery, observation, and learning foundations have been implemented and tested.

The project is **not yet a complete operating system**.

### Current progress

| Area | Status |
|---|---|
| Task management | ✅ Implemented |
| Workflow planning | ✅ Implemented |
| Tool registry | ✅ Implemented |
| Tool discovery | ✅ Implemented |
| Safe tool execution | ✅ Implemented |
| Risk classification | ✅ Implemented |
| Permission system | ✅ Implemented |
| Execution observation | ✅ Implemented |
| Failure recovery | ✅ Implemented |
| Experience / learning engine | ✅ Implemented |
| Experience-aware AI planning | ✅ Implemented |
| Real computer control | 🚧 In development |
| Browser automation | ⏳ Planned |
| Graphical interface | ⏳ Planned |
| Voice interface | ⏳ Planned |
| Deeper Linux integration | ⏳ Planned |
| End-to-end prototype | ⏳ Planned |

---

# Vision

The long-term vision of Converted OS is to allow a user to provide an outcome instead of a sequence of instructions.

For example:

> **"Create a website for my project."**

Instead of requiring the user to specify every step, Converted OS should eventually be able to:

```text
Understand the goal
        ↓
Create a temporary workflow
        ↓
Open the required applications
        ↓
Create project files
        ↓
Write the code
        ↓
Run the project
        ↓
Open and inspect the result
        ↓
Detect problems
        ↓
Adapt the workflow
        ↓
Apply corrections
        ↓
Verify the result
        ↓
Present the result to the user
        ↓
Learn from the experience
