from backend.app import model as model_module
from backend.app import transformer_model as tm
from backend.app import factcheck as fc


def test_predict_text_model():
    m = model_module.load_or_train_model()
    label, score = model_module.predict_text(m, 'This is a clearly fake claim')
    assert label in m.classes_
    assert isinstance(score, float)


def test_transformer_predict_mock(monkeypatch):
    def fake_predict(text):
        return ('fake', 0.92, {'labels': ['fake', 'real'], 'scores': [0.92, 0.08]})

    monkeypatch.setattr(tm, 'predict_zero_shot', fake_predict)
    label, score, details = tm.predict_zero_shot('Some claim')
    assert label == 'fake'
    assert score == 0.92


def test_factcheck_local():
    res = fc.fact_check_text('Claim about policy.')
    assert 'claims' in res
    assert isinstance(res['claims'], list)
    assert res['claims'][0]['claim'] == 'Claim about policy.'
    assert 'top_matches' in res['claims'][0]


def test_factcheck_death_query_false(monkeypatch):
    def fake_search(query, count=3):
        return [
            {'title': 'Narendra Modi', 'snippet': 'Narendra Damodardas Modi is an Indian politician.', 'url': 'https://en.wikipedia.org/?curid=444222', 'score': 1.0},
            {'title': 'Narendra Modi Stadium', 'snippet': 'Narendra Modi Stadium is an international cricket stadium.', 'url': 'https://en.wikipedia.org/?curid=80201506', 'score': 0.5},
        ]

    monkeypatch.setattr(fc, 'search_wikipedia', fake_search)
    res = fc.fact_check_text('is modi dead')
    assert res['claims'][0]['verdict'] == 'Likely false'
    assert res['claims'][0]['source'] == 'wikipedia'
    assert 'support_words' in res['claims'][0]
