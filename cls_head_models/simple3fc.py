import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F

class feat_classifier(torch.nn.Module):
    def __init__(self, num_classes, input_shape = [256, 7, 7], hidden_dim=1024, cls_fc_bias=True):
        super(feat_classifier, self).__init__()

        self.cls_last_dim = input_shape[0]*input_shape[1]*input_shape[2]

        self.fc1 = nn.Linear(self.cls_last_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc_classifier = nn.Linear(hidden_dim, num_classes, bias=cls_fc_bias)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc_classifier(x)

        return x

class simple3fc(torch.nn.Module):

    def __init__(self, num_classes=1231, cls_fc_bias=True):
        super(simple3fc, self).__init__()

        self.feat_classifier = feat_classifier(num_classes=num_classes, hidden_dim=1024, cls_fc_bias=cls_fc_bias).cuda()

    def forward(self, input):
        logits = self.feat_classifier(input)
        return logits



# def ncm_sq_dist_bt_norm(a,b):
#     anorm = tf.reshape(tf.reduce_sum(tf.square(a), 1),[-1, 1])
#     bnorm = tf.reshape(tf.reduce_sum(tf.square(b), 0),[1, -1])
#     d     = -2*tf.matmul(a,b,transpose_b=False)+anorm + bnorm
#     return d, anorm
#
# def ncm_sq_dist_bt(a,b):
#     d, bnorm = ncm_sq_dist_bt_norm(a,b)
#     return d

