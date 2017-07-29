import numpy as np

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


def test_bpr_hybrid():

    interactions = movielens.get_movielens_dataset('100K')

    normalized_timestamps = _min_max_scale(interactions.timestamps).reshape(-1, 1)

    interactions.context_features = normalized_timestamps / 100

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='bpr',
                                       n_iter=30,
                                       batch_size=256,
                                       learning_rate=1e-2,
                                       l2=1e-6)
    model.fit(train, verbose=True)
    print(model)

    mrr = mrr_score(model, test, train=train).mean()

    assert mrr > 0.07


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


def test_pointwise_synthetic_hybrid():

    interactions = synthetic.generate_content_based(random_state=RANDOM_STATE)

    train, test = random_train_test_split(interactions,
                                          random_state=RANDOM_STATE)

    model = ImplicitFactorizationModel(loss='bpr',
                                       n_iter=10,
                                       batch_size=1024,
                                       learning_rate=1e-2,
                                       l2=0.0)

    model.fit(train, verbose=True)
    print(model._net)

    # test.context_features *= 0
    # test.user_features *= 0
    # test.item_features *= 0

    mrr = mrr_score(model, test, train=train).mean()

    print('MRR {}'.format(mrr))

    assert mrr > 0.05
