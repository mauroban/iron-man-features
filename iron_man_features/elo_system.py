import json
import logging
from typing import Tuple

import pandas as pd


class EloSystem:
    def __init__(
        self,
        base_k_factor: int = 32,
        boost_threshold: int = 6,
        boost_factor: float = 1,
        postfix: str = "",
        first_from_rank: bool = True,
        boost_diff: bool = False,
        mean_elo: float = 1500,
        decay_rate: float = 0.995,
    ):
        """
        Initialize the EloSystem.

        Args:
            base_k_factor (int): The base K-factor for Elo updates.
            boost_threshold (int): Score difference threshold to trigger
                                   Elo variation boost.
            boost_factor (float): Multiplier when score difference exceeds
                                  the threshold.
            postfix (str): Postfix to append to Elo keys.
            first_from_rank (bool): Use initial Elo based on rank.
            boost_diff (bool): Boost Elo change based on score difference.
            mean_elo (float): The mean Elo rating for regression.
            decay_rate (float): The rate at which Elo ratings decay over time.
        """
        self.base_k_factor = base_k_factor
        self.boost_threshold = boost_threshold
        self.boost_factor = boost_factor
        self.ratings = {}
        self.postfix = postfix
        self.first_from_rank = first_from_rank
        self.boost_diff = boost_diff
        self.mean_elo = mean_elo
        self.decay_rate = decay_rate
        self.team_game_counts = {}
        self.last_played = {}
        logging.info(
            "Elo System initiated\n"
            f"base_k_factor: {base_k_factor}\n"
            f"boost_threshold: {boost_threshold}\n"
            f"boost_factor: {boost_factor}\n"
            f"postfix: {postfix}\n"
            f"first_from_rank: {first_from_rank}\n"
            f"boost_diff: {boost_diff}\n"
            f"mean_elo: {mean_elo}\n"
            f"decay_rate: {decay_rate}"
        )

    def default_elo(self, rank) -> float:
        if not self.first_from_rank:
            return self.mean_elo
        if pd.isna(rank):
            return self.mean_elo - 150
        base_elo = {
            5: self.mean_elo + 100,
            20: self.mean_elo + 50,
            50: self.mean_elo,
            100: self.mean_elo - 50,
            200: self.mean_elo - 100,
            500: self.mean_elo - 150,
        }
        for i in sorted(base_elo.keys()):
            if int(rank) <= i:
                return base_elo[i]
        return self.mean_elo - 150

    def get_dynamic_k(self, team_id: int, current_date: pd.Timestamp) -> float:
        num_games = self.team_game_counts.get(team_id, 0)
        last_played = self.last_played.get(team_id, current_date)
        days_inactive = (current_date - last_played).days
        if num_games < 5:
            base_k = self.base_k_factor * 2  # Higher K-factor for new teams
        elif num_games < 20:
            base_k = self.base_k_factor
        else:
            base_k = self.base_k_factor / 2  # Lower K-factor for established teams

        # Adjust K-factor based on days inactive
        if days_inactive <= 7:
            k_multiplier = 1.0
        elif days_inactive <= 30:
            # Increase linearly from 1.0 to 1.5 as days_inactive goes from 7 to 30
            k_multiplier = 1.0 + ((days_inactive - 7) / (30 - 7)) * 0.5
        else:
            k_multiplier = 1.5  # Cap the multiplier at 1.5

        dynamic_k = base_k * k_multiplier
        return dynamic_k

    def regress_to_mean(self, team_id: int, elo_hash: str) -> None:
        team_elo = self.ratings[team_id][elo_hash]
        num_games = self.team_game_counts.get(team_id, 0)
        weight = min(1, 5 / (num_games + 1))
        self.ratings[team_id][elo_hash] = (
            1 - weight
        ) * team_elo + weight * self.mean_elo

    def apply_decay(
        self, team_id: int, elo_hash: str, current_date: pd.Timestamp
    ) -> None:
        last_played = self.last_played.get(team_id, current_date)
        days_inactive = (current_date - last_played).days
        decay_factor = self.decay_rate**days_inactive
        self.ratings[team_id][elo_hash] *= decay_factor
        self.last_played[team_id] = current_date

    def calc_expected_score(self, elo_team: float, elo_opponent: float) -> float:
        return 1 / (1 + 10 ** ((elo_opponent - elo_team) / 400))

    def determine_match_outcome(
        self, team_score: int, opponent_score: int
    ) -> Tuple[float, float]:
        if team_score > opponent_score:
            return 1, 0
        elif team_score < opponent_score:
            return 0, 1
        else:
            # For ties or overtime, adjust as needed
            return 0.5, 0.5

    def calc_boost_multiplier(self, team_score: int, opponent_score: int) -> float:
        score_difference = abs(team_score - opponent_score)
        if score_difference >= self.boost_threshold:
            return self.boost_factor
        return 1

    def calc_boost_diff(self, team_score: int, opponent_score: int) -> float:
        if self.boost_diff:
            score_difference = abs(team_score - opponent_score)
            return self.base_k_factor / 10 * score_difference
        return 0

    def update_elo(
        self,
        team_id: int,
        opponent_id: int,
        team_score: int,
        opponent_score: int,
        elo_hash: str,
        team_rank: int,
        opponent_rank: int,
        current_date: pd.Timestamp,
    ) -> None:
        team_elo = self.ratings.setdefault(team_id, {}).setdefault(
            elo_hash, self.default_elo(team_rank)
        )
        opponent_elo = self.ratings.setdefault(opponent_id, {}).setdefault(
            elo_hash, self.default_elo(opponent_rank)
        )

        # Apply decay to both teams
        self.apply_decay(team_id, elo_hash, current_date)
        self.apply_decay(opponent_id, elo_hash, current_date)

        if team_score is None or opponent_score is None:
            logging.warning(
                f"Score is null for game {team_id} x {opponent_id}, aborting elo calc"
            )
            return

        # Determine the match result
        team_actual_score, opponent_actual_score = self.determine_match_outcome(
            team_score, opponent_score
        )

        # Calculate the expected scores
        expected_team_score = self.calc_expected_score(team_elo, opponent_elo)
        expected_opponent_score = 1 - expected_team_score

        # Calculate the boost multiplier based on the score difference
        boost_multiplier = self.calc_boost_multiplier(team_score, opponent_score)
        boost_diff = self.calc_boost_diff(team_score, opponent_score)

        # Get dynamic K-factors
        team_k = self.get_dynamic_k(team_id, current_date)
        opponent_k = self.get_dynamic_k(opponent_id, current_date)

        # Apply Elo updates with the boost multiplier
        team_elo_change = team_k * boost_multiplier * (
            team_actual_score - expected_team_score
        ) + boost_diff * (1 if team_actual_score > expected_team_score else -1)
        opponent_elo_change = opponent_k * boost_multiplier * (
            opponent_actual_score - expected_opponent_score
        ) + boost_diff * (1 if opponent_actual_score > expected_opponent_score else -1)

        # Update the ratings
        self.ratings[team_id][elo_hash] += team_elo_change
        self.ratings[opponent_id][elo_hash] += opponent_elo_change

        # Increment game counts
        self.team_game_counts[team_id] = self.team_game_counts.get(team_id, 0) + 1
        self.team_game_counts[opponent_id] = (
            self.team_game_counts.get(opponent_id, 0) + 1
        )

        # Regress ratings to the mean for both teams
        self.regress_to_mean(team_id, elo_hash)
        self.regress_to_mean(opponent_id, elo_hash)

    def process_game(self, game: pd.Series) -> None:
        for elo_hash in [
            f"overall_elo{self.postfix}",
            f"{game['played_map'].lower()}_elo{self.postfix}",
        ]:
            self.update_elo(
                team_id=game["roster_hash"],
                opponent_id=game["roster_hash_op"],
                team_score=game["score"],
                opponent_score=game["score_op"],
                elo_hash=elo_hash,
                team_rank=game["hltv_rank"],
                opponent_rank=game["hltv_rank_op"],
                current_date=game["start_date"],
            )

    def calculate_elo(self, games: pd.DataFrame) -> None:
        elo_rows = []
        match_ratings = {}
        last_match_id = None
        for _, game in games.sort_values("start_date").iterrows():
            if not last_match_id or last_match_id != game["match_id"]:
                match_ratings = self.ratings.copy()
                last_match_id = game["match_id"]
            for roster_hash in [game["roster_hash"], game["roster_hash_op"]]:
                elo_row = {
                    "game_id": game["game_id"],
                    "roster_hash": roster_hash,
                }
                elo_row.update(match_ratings.get(roster_hash, {}))
                elo_rows.append(elo_row)
            self.process_game(game)

        self.elo_table = pd.DataFrame.from_records(elo_rows)

    def add_elos_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.merge(
            self.elo_table,
            how="left",
            left_on=["roster_hash", "game_id"],
            right_on=["roster_hash", "game_id"],
        )
        return df

    def save_ratings(self):
        with open("elo_ratings.json", "w") as f:
            json.dump(self.ratings, f, indent=4)


def calculate_elos(
    df: pd.DataFrame, elo_games_df: pd.DataFrame, elo_system: EloSystem
) -> pd.DataFrame:
    elo_system.calculate_elo(games=elo_games_df)
    logging.info(
        f"Calculated elos for {len(elo_system.ratings.keys())} team rosters using "
        f"{len(elo_games_df)} game results"
    )
    df = elo_system.add_elos_to_df(df)

    new_matches = pd.isna(df["won"])
    elo_columns = [c for c in df.columns if f"elo{elo_system.postfix}" in c]

    for c in elo_columns:
        for i, new_match in df.loc[new_matches].iterrows():
            df.at[i, c] = elo_system.ratings.get(new_match["roster_hash"], {}).get(c)
    return df
