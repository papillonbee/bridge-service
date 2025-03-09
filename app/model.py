from enum import Enum
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class SnakeCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
        from_attributes = True,
    )

class BidEnum(Enum):
    PASS = "P"

    ONE_CLUB = "1C"
    ONE_DIAMOND = "1D"
    ONE_HEART = "1H"
    ONE_SPADE = "1S"
    ONE_NO_TRUMP = "1NT"

    TWO_CLUB = "2C"
    TWO_DIAMOND = "2D"
    TWO_HEART = "2H"
    TWO_SPADE = "2S"
    TWO_NO_TRUMP = "2NT"

    THREE_CLUB = "3C"
    THREE_DIAMOND = "3D"
    THREE_HEART = "3H"
    THREE_SPADE = "3S"
    THREE_NO_TRUMP = "3NT"

    FOUR_CLUB = "4C"
    FOUR_DIAMOND = "4D"
    FOUR_HEART = "4H"
    FOUR_SPADE = "4S"
    FOUR_NO_TRUMP = "4NT"
    
    FIVE_CLUB = "5C"
    FIVE_DIAMOND = "5D"
    FIVE_HEART = "5H"
    FIVE_SPADE = "5S"
    FIVE_NO_TRUMP = "5NT"
    
    SIX_CLUB = "6C"
    SIX_DIAMOND = "6D"
    SIX_HEART = "6H"
    SIX_SPADE = "6S"
    SIX_NO_TRUMP = "6NT"

    SEVEN_CLUB = "7C"
    SEVEN_DIAMOND = "7D"
    SEVEN_HEART = "7H"
    SEVEN_SPADE = "7S"
    SEVEN_NO_TRUMP = "7NT"

class CardEnum(Enum):
    TWO_CLUB = "2C"
    THREE_CLUB = "3C"
    FOUR_CLUB = "4C"
    FIVE_CLUB = "5C"
    SIX_CLUB = "6C"
    SEVEN_CLUB = "7C"
    EIGHT_CLUB = "8C"
    NINE_CLUB = "9C"
    TEN_CLUB = "10C"
    JACK_CLUB = "JC"
    QUEEN_CLUB = "QC"
    KING_CLUB = "KC"
    ACE_CLUB = "AC"

    TWO_DIAMOND = "2D"
    THREE_DIAMOND = "3D"
    FOUR_DIAMOND = "4D"
    FIVE_DIAMOND = "5D"
    SIX_DIAMOND = "6D"
    SEVEN_DIAMOND = "7D"
    EIGHT_DIAMOND = "8D"
    NINE_DIAMOND = "9D"
    TEN_DIAMOND = "10D"
    JACK_DIAMOND = "JD"
    QUEEN_DIAMOND = "QD"
    KING_DIAMOND = "KD"
    ACE_DIAMOND = "AD"

    TWO_HEART = "2H"
    THREE_HEART = "3H"
    FOUR_HEART = "4H"
    FIVE_HEART = "5H"
    SIX_HEART = "6H"
    SEVEN_HEART = "7H"
    EIGHT_HEART = "8H"
    NINE_HEART = "9H"
    TEN_HEART = "10H"
    JACK_HEART = "JH"
    QUEEN_HEART = "QH"
    KING_HEART = "KH"
    ACE_HEART = "AH"

    TWO_SPADE = "2S"
    THREE_SPADE = "3S"
    FOUR_SPADE = "4S"
    FIVE_SPADE = "5S"
    SIX_SPADE = "6S"
    SEVEN_SPADE = "7S"
    EIGHT_SPADE = "8S"
    NINE_SPADE = "9S"
    TEN_SPADE = "10S"
    JACK_SPADE = "JS"
    QUEEN_SPADE = "QS"
    KING_SPADE = "KS"
    ACE_SPADE = "AS"

class PlayerBid(SnakeCaseModel):
    player_id: str
    bid: BidEnum | None

class PlayerTrick(SnakeCaseModel):
    player_id: str
    trick: CardEnum
    win: bool

class PlayerScore(SnakeCaseModel):
    player_id: str
    score: int
    won: bool

class GameTrick(SnakeCaseModel):
    player_tricks: list[PlayerTrick]
