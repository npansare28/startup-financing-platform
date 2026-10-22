# ML Recommendation Engine — V1

## Install

Inside the backend virtual environment:

```bash
pip install scikit-learn numpy
```

## Test

From this `ml` directory:

```bash
python test_recommender.py
```

The test uses fake in-memory profiles. It does not touch MySQL and does not modify your existing Flask application.

## What V1 does

It calculates an interpretable compatibility score using:

- Industry match — 30%
- Startup stage match — 20%
- Funding/investment fit — 25%
- Location match — 10%
- TF-IDF text similarity — 15%

The score is currently an engineering baseline, not a trained prediction model.

## Next integration

After V1 is verified:

1. Load pitcher/investor profiles from MySQL.
2. Convert them into the same feature format.
3. Call `rank_investors()` or `rank_pitchers()`.
4. Return `compatibility_score` with recommendations.
5. Later collect swipe/match outcomes and train learned weights/model.
