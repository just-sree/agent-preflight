from agent_preflight.models import ActionPayload, PolicyDecision


class BasePolicy:
    name = "base"

    def evaluate(self, payload: ActionPayload) -> PolicyDecision:
        return PolicyDecision(
            allowed=True,
            reason="Allowed by default",
            policy_name=self.name,
        )


class BlockActionNamesPolicy(BasePolicy):
    name = "block_action_names"

    def __init__(self, blocked_actions: set[str]):
        self.blocked_actions = blocked_actions

    def evaluate(self, payload: ActionPayload) -> PolicyDecision:
        if payload.action_name in self.blocked_actions:
            return PolicyDecision(
                allowed=False,
                reason="Action is blocked by policy",
                policy_name=self.name,
            )

        return PolicyDecision(
            allowed=True,
            reason="Allowed by policy",
            policy_name=self.name,
        )
