import pandas as pd
import numpy as np
from src.engine.randomization import Randomizer

class ExperimentSimulator:
    @staticmethod
    def generate_data(
        n_users: int,
        exp_id: str,
        true_p_a: float,
        true_p_b: float,
        seed: int = 42,
        bounce_a: float = 0.32,
        bounce_b: float = 0.335,
        avg_order_value_a: float = 82.0,
        avg_order_value_b: float = 80.0,
    ) -> pd.DataFrame:
        """
        Creates a synthetic product experiment dataset.

        The extra revenue and bounce fields are guardrail-friendly proxies that
        make the example read like a product analytics case study.
        """
        rng = np.random.default_rng(seed)
        data = []
        randomizer = Randomizer()

        for i in range(n_users):
            user_id = f"user_{i:05d}"
            # 1. Assign variant using our deterministic hashing
            variant = randomizer.get_variant(user_id, exp_id)
            
            # 2. Simulate conversion based on the 'True' probability of that group
            # Group B usually has the 'lift'
            prob = true_p_b if variant == "B" else true_p_a
            converted = rng.binomial(1, prob)

            bounce_prob = bounce_b if variant == "B" else bounce_a
            bounced = rng.binomial(1, bounce_prob)

            avg_order_value = avg_order_value_b if variant == "B" else avg_order_value_a
            order_value = max(0, rng.normal(avg_order_value, 18)) if converted else 0.0
            
            data.append({
                "user_id": user_id,
                "variant": variant,
                "converted": converted,
                "bounced": bounced,
                "order_value": round(order_value, 2),
                "revenue": round(order_value, 2),
            })
            
        return pd.DataFrame(data)
