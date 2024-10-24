import json
import logging
from typing import Dict, Tuple

import pandas as pd


class EloSystem:
    def __init__(
        self,
        k_factor: int = 32,
        boost_threshold: int = 6,
        boost_factor: float = 1,
        postfix: str = "",
        first_from_rank: bool = True,
    ):
        """
        Initialize the EloSystem.

        Args:
            default_elo (float): Starting Elo rating for new teams.
            k_factor (int): The standard K-factor for Elo updates.
            boost_threshold (int): Score difference threshold to trigger Elo variation
            boost.
            boost_factor (float): Multiplier to apply when score difference exceeds the
            threshold.
        """
        self.k_factor = k_factor
        self.boost_threshold = boost_threshold
        self.boost_factor = boost_factor
        self.ratings = {}
        self.postfix = postfix
        self.first_from_rank = first_from_rank
        logging.info(
            "Elo System initiated\n"
            f"k_factor: {k_factor}\n"
            f"boost_threshold: {boost_threshold}\n"
            f"boost_factor: {boost_factor}\n"
            f"postfix: {postfix}\n"
            f"first_from_rank: {first_from_rank}"
        )

    def default_elo(self, rank) -> float:
        if not self.first_from_rank:
            return 1500
        if pd.isna(rank):
            return 1350
        base_elo = {
            5: 1600,
            20: 1550,
            50: 1500,
            100: 1450,
            200: 1400,
            500: 1350,
        }
        for i in base_elo.keys():
            if int(rank) <= i:
                return base_elo[i]
        return 1350

    def calc_expected_score(self, elo_team: float, elo_opponent: float) -> float:
        """
        Calculate the expected score of a team based on its Elo rating and the
        opponent's Elo rating.
        """
        return 1 / (1 + 10 ** ((elo_opponent - elo_team) / 400))

    def determine_match_outcome(
        self, team_score: int, opponent_score: int
    ) -> Tuple[float, float]:
        """
        Determine the match outcome in terms of actual Elo scores.
        """
        if team_score > opponent_score:
            return 1, 0
        elif team_score < opponent_score:
            return 0, 1
        else:
            return 0.5, 0.5

    def calc_boost_multiplier(self, team_score: int, opponent_score: int) -> float:
        """
        Calculate the boost multiplier based on the score difference.

        Args:
            team_score (int): The score of the team.
            opponent_score (int): The score of the opponent.

        Returns:
            float: Boost multiplier, 1 if no boost is applied.
        """
        score_difference = abs(team_score - opponent_score)
        if score_difference >= self.boost_threshold:
            return self.boost_factor
        return 1

    def update_elo(
        self,
        team_id: int,
        opponent_id: int,
        team_score: int,
        opponent_score: int,
        elo_hash: str,
        team_rank: int,
        opponent_rank: int,
    ) -> None:
        """# noqa
        Update Elo ratings for both teams based on the match result, applying a boost if necessary.

        Args:
            ratings (Dict): The Elo rating dictionary to update (overall, map-specific, or side-specific).
            team_key (Tuple): The key for the team's Elo rating in the dictionary.
            opponent_key (Tuple): The key for the opponent's Elo rating in the dictionary.
            team_actual_score (float): The actual score of the team (1 for win, 0 for loss, 0.5 for draw).
            opponent_actual_score (float): The actual score of the opponent.
            team_score (int): The score of the team.
            opponent_score (int): The score of the opponent.
        """
        team_elo = self.ratings.setdefault(team_id, {}).setdefault(
            elo_hash, self.default_elo(team_rank)
        )
        opponent_elo = self.ratings.setdefault(opponent_id, {}).setdefault(
            elo_hash, self.default_elo(opponent_rank)
        )

        # Determine the match result
        team_actual_score, opponent_actual_score = self.determine_match_outcome(
            team_score, opponent_score
        )

        # Calculate the expected scores
        expected_team_score = self.calc_expected_score(team_elo, opponent_elo)
        expected_opponent_score = self.calc_expected_score(opponent_elo, team_elo)

        # Calculate the boost multiplier based on the score difference
        boost_multiplier = self.calc_boost_multiplier(team_score, opponent_score)

        # Apply Elo updates with the boost multiplier
        self.ratings[team_id][elo_hash] += (
            self.k_factor * boost_multiplier * (team_actual_score - expected_team_score)
        )
        self.ratings[opponent_id][elo_hash] += (
            self.k_factor
            * boost_multiplier
            * (opponent_actual_score - expected_opponent_score)
        )

    def process_game(self, game: pd.Series) -> None:
        """
        Process a single game to update overall Elo, map-specific Elo,
        and side-specific Elo.
        """
        for elo_hash in [
            f"overall_elo{self.postfix}",
            f"{game["played_map"].lower()}_elo{self.postfix}",
        ]:
            self.update_elo(
                team_id=game["roster_hash"],
                opponent_id=game["roster_hash_op"],
                team_score=game["score"],
                opponent_score=game["score_op"],
                elo_hash=elo_hash,
                team_rank=game["hltv_rank"],
                opponent_rank=game["hltv_rank_op"],
            )

        for side in ["ct", "tr"]:
            self.update_elo(
                team_id=game["roster_hash"],
                opponent_id=game["roster_hash_op"],
                team_score=game[f"score_{side}"],
                opponent_score=game[f"score_{side}_op"],
                elo_hash=f"{game["played_map"].lower()}_{side}_elo{self.postfix}",
                team_rank=game["hltv_rank"],
                opponent_rank=game["hltv_rank_op"],
            )

    def calculate_elo(self, games: pd.DataFrame) -> Tuple[
        Dict[int, float],
        Dict[Tuple[int, str], float],
        Dict[Tuple[int, str, str], float],
    ]:
        """
        Calculate Elo ratings for all games.

        Args:
            games (pd.DataFrame): DataFrame containing game results.

        Returns:
            Tuple containing:
            - overall_elo: Dictionary of overall Elo ratings.
            - map_elo: Dictionary of map-specific Elo ratings.
            - side_map_elo: Dictionary of side-specific Elo ratings.
        """
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
                # print(elo_row)
                elo_rows.append(elo_row)
            self.process_game(game)

        self.elo_table = pd.DataFrame.from_records(elo_rows)

    def add_elos_to_df(self, df):
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
            df.at[i, c] = elo_system.ratings.get(new_match["roster_hash"]).get(c)

    return df
