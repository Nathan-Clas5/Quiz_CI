import pytest
class EngagementEngine:
    def __init__(self, user_handle, verified=False):
        self.user_handle = user_handle
        self.score = 0.0
        self.verified = verified

    def process_interaction(self, itype, count=1):
        if count < 0: raise ValueError("Negative count")
        weights = {"like": 1, "comment": 5, "share": 10}
        if itype not in weights: return False
        
        points = weights[itype] * count
        if self.verified: points *= 1.5
        self.score += points
        return True

    def get_tier(self):
        if self.score < 100: return "Newbie"
        if self.score <= 1000: return "Influencer"
        return "Icon"

    def apply_penalty(self, report_count):
        if report_count > 10: self.verified = False
        reduction = self.score * (0.20 * report_count)
        self.score = max(0, self.score - reduction) 

@pytest.fixture
def engine():
    return EngagementEngine(user_handle="test_user")

def test_initial_score_and_tier():
    engine = EngagementEngine("user1")
    assert engine.score == 0.0
    assert engine.get_tier() == "Newbie"

def test_process_interaction_like():
    engine = EngagementEngine("user2")
    result = engine.process_interaction("like", 3)
    assert result is True
    assert engine.score == 3.0

def test_process_interaction_comment():
    engine = EngagementEngine("user3")
    result = engine.process_interaction("comment", 2)
    assert result is True
    assert engine.score == 10.0  # 5 * 2

def test_process_interaction_share():
    engine = EngagementEngine("user4")
    result = engine.process_interaction("share", 1)
    assert result is True
    assert engine.score == 10.0

def test_process_interaction_invalid_type():
    engine = EngagementEngine("user5")
    result = engine.process_interaction("subscribe", 1)
    assert result is False
    assert engine.score == 0

def test_process_interaction_negative_count():
    engine = EngagementEngine("user6")
    with pytest.raises(ValueError):
        engine.process_interaction("like", -1)

def test_tier_thresholds():
    engine = EngagementEngine("user7")
    # below 100
    engine.score = 99
    assert engine.get_tier() == "Newbie"
    # exactly 100
    engine.score = 100
    assert engine.get_tier() == "Influencer"
    # above 100
    engine.score = 500
    assert engine.get_tier() == "Influencer"
    # above 1000
    engine.score = 1001
    assert engine.get_tier() == "Icon"

def test_apply_penalty_no_report():
    engine = EngagementEngine("user8")
    engine.score = 500
    engine.apply_penalty(0)
    assert engine.score == 500
    assert engine.verified is False  # no penalty, so verified remains unchanged

def test_apply_penalty_small_report():
    engine = EngagementEngine("user9")
    engine.score = 1000
    engine.verified = True
    engine.apply_penalty(5)  # report count <= 10
    expected_score = 1000 - (1000 * 0.20 * 5)
    assert engine.score == expected_score
    assert engine.verified is True

def test_apply_penalty_large_report():
    engine = EngagementEngine("user10")
    engine.score = 1000
    engine.verified = True
    engine.apply_penalty(15)  # report count > 10
    assert engine.verified is False
    expected_score = max(0, 1000 - (1000 * 0.20 * 15))
    assert engine.score == expected_score

def test_score_never_negative():
    engine = EngagementEngine("user11")
    engine.score = 10
    engine.apply_penalty(10)  # 10 * 0.2 * 10 = 20, should not go below zero
    assert engine.score == 0