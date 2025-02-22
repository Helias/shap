""" Tests for Explainer class.
"""

import pytest
import sklearn

import shap


def test_explainer_to_permutationexplainer():
    """Checks that Explainer maps to PermutationExplainer as expected."""

    X_train, X_test, y_train, _ = sklearn.model_selection.train_test_split(*shap.datasets.adult(), test_size=0.1, random_state=0)
    lr = sklearn.linear_model.LogisticRegression(solver="liblinear")
    lr.fit(X_train, y_train)

    explainer = shap.Explainer(lr.predict_proba, masker=X_train)
    assert isinstance(explainer, shap.PermutationExplainer)

    # ensures a proper error message is raised if a masker is not provided (GH #3310)
    with pytest.raises(
        ValueError,
        match=r"masker cannot be None",
    ):
        explainer = shap.Explainer(lr.predict_proba)
        _ = explainer(X_test)


def test_wrapping_for_text_to_text_teacher_forcing_model():
    """ This tests using the Explainer class to auto wrap a masker in a text to text scenario.
    """

    transformers = pytest.importorskip("transformers")

    def f(x): # pylint: disable=unused-argument
        pass

    tokenizer = transformers.AutoTokenizer.from_pretrained("gpt2")
    model = transformers.AutoModelForCausalLM.from_pretrained("gpt2")
    wrapped_model = shap.models.TeacherForcing(f, similarity_model=model, similarity_tokenizer=tokenizer)
    masker = shap.maskers.Text(tokenizer, mask_token="...")

    explainer = shap.Explainer(wrapped_model, masker, seed=1)

    assert shap.utils.safe_isinstance(explainer.masker, "shap.maskers.OutputComposite")

def test_wrapping_for_topk_lm_model():
    """ This tests using the Explainer class to auto wrap a masker in a language modelling scenario.
    """

    transformers = pytest.importorskip("transformers")

    tokenizer = transformers.AutoTokenizer.from_pretrained("gpt2")
    model = transformers.AutoModelForCausalLM.from_pretrained("gpt2")
    wrapped_model = shap.models.TopKLM(model, tokenizer)
    masker = shap.maskers.Text(tokenizer, mask_token="...")

    explainer = shap.Explainer(wrapped_model, masker, seed=1)

    assert shap.utils.safe_isinstance(explainer.masker, "shap.maskers.FixedComposite")
