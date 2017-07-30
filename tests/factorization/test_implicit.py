import numpy as np

import pytest

from spotlight.cross_validation import random_train_test_split
from spotlight.datasets import movielens, synthetic
from spotlight.evaluation import mrr_score
from spotlight.factorization.implicit import ImplicitFactorizationModel


RANDOM_STATE = np.random.RandomState(42)


def _min_max_scale(arr):

    arr_min = arr.min()
    arr_max = arr.max()

    return (arr - arr_min) / (arr_max - arr_min)


def test_pointwise():

    interactions = movielens.get_movielens_dataset('100K')

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='pointwise',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=1e-6)
    model.fit(train)

    mrr = mrr_score(model, test, train=train).mean()

    assert mrr > 0.05


def test_bpr():

    interactions = movielens.get_movielens_dataset('100K')

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='bpr',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=1e-6)
    model.fit(train)

    mrr = mrr_score(model, test, train=train).mean()

    assert mrr > 0.07


@pytest.mark.parametrize('use_timestamps, expected_mrr', [
    (True, 0.06),
    (False, 0.060),
])
def test_bpr_hybrid(use_timestamps, expected_mrr):

    interactions = movielens.get_movielens_dataset('100K')

    if use_timestamps:
        normalized_timestamps = (_min_max_scale(interactions.timestamps)
                                 .reshape(-1, 1))
        interactions.context_features = normalized_timestamps / 100

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='bpr',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=1e-6)
    model.fit(train, verbose=True)
    print(model)

    mrr = mrr_score(model, test, train=train, average_per_context=False).mean()

    print('MRR {}'.format(mrr))

    assert mrr > expected_mrr


def test_hinge():

    interactions = movielens.get_movielens_dataset('100K')

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='hinge',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=1e-6)
    model.fit(train)

    mrr = mrr_score(model, test, train=train).mean()

    assert mrr > 0.07


def test_adaptive_hinge():

    interactions = movielens.get_movielens_dataset('100K')

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='adaptive_hinge',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=1e-6)
    model.fit(train)

    mrr = mrr_score(model, test, train=train).mean()

    assert mrr > 0.07


@pytest.mark.parametrize('use_features, expected_mrr', [
    (False, 0.01),
    (True, 0.11),
])
def test_synthetic_hybrid(use_features, expected_mrr):

    interactions = synthetic.generate_content_based(random_state=RANDOM_STATE)

    if not use_features:
        interactions.user_features = None
        interactions.context_features = None
        interactions.item_features = None

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='bpr',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=0.0,
                                       random_state=RANDOM_STATE)

    model.fit(train, verbose=True)
    print(model._net)

    mrr = mrr_score(model, test, train=train, average_per_context=False).mean()

    print('MRR {}'.format(mrr))

    assert mrr > expected_mrr
