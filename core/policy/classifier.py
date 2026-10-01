from core.policy.policy import (
    Action,
    RiskLevel,
)


class ActionClassifier:

    def classify(
        self,
        name: str,
        description: str,
    ) -> Action:

        text = (
            f"{name} {description}"
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        if any(
            keyword in text
            for keyword in [
                "delete system",
                "format disk",
                "shutdown system",
                "shutdown computer",
                "remove system",
                "modify kernel",
                "reboot system",
            ]
        ):
            risk = RiskLevel.HIGH

        elif any(
            keyword in text
            for keyword in [
                "delete",
                "remove",
                "install",
                "uninstall",
                "download",
                "network",
                "execute command",
                "run command",
            ]
        ):
            risk = RiskLevel.MEDIUM

        else:
            risk = RiskLevel.LOW

        return Action(
            name=name,
            description=description,
            risk=risk,
        )
