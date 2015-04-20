import cudarray as ca
from ..feed_forward.loss import Loss


class ContrastiveLoss(Loss):
    def __init__(self, margin=1.0):
        self.name = 'contrastive'
        self.margin = margin
        self._last_x1 = None
        self._last_x2 = None
        self._last_dists = None

    def predict(self, x1, x2):
        if self._last_x1 is not x1 or self._last_x2 is not x2:
            self._last_dists = ca.sum((x1-x2)**2, axis=1, keepdims=True)
            self._last_x1 = x1
            self._last_x2 = x2
        return self._last_dists

    def input_grad(self, target, x1, x2):
        dists = self.predict(x1, x2)
        target = ca.reshape(target, target.shape+(1,))

        grad_dists1 = 2*(x1-x2)
        genuine = target*grad_dists1
        imposter = (1-target)*(-grad_dists1)
        non_saturated_imposters = self.margin-dists > 0.0
        imposter *= non_saturated_imposters
        grad_x1 = genuine + imposter
        return grad_x1, -grad_x1

    def loss(self, target, x1, x2):
        dists = self.predict(x1, x2)
        return target*dists + (1-target)*ca.maximum(self.margin-dists, 0)

    def output_shape(self, input_shape):
        return (input_shape[0],)
