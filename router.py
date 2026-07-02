def route_question(state):
    return "next" if not state.get("completed") else "done"
