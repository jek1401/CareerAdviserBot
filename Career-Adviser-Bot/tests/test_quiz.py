from utils.quiz import get_interests, get_professions_by_interests

def test_get_interests():
    interests = get_interests()
    assert isinstance(interests, list)
    assert len(interests) > 0
    assert 'дизайн' in interests

def test_get_professions():
    professions = get_professions_by_interests(['дизайн'])
    assert len(professions) > 0
    titles = [p[1] for p in professions]
    assert 'UX-дизайнер' in titles or 'Графический дизайнер' in titles