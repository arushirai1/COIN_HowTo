# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import math

import numpy as np
import torch
import torch.nn as nn
import pickle

__all__ = ['RobertaCaptions', 'roberta_model']


class RobertaCaptions(nn.Module):
    def __init__(self, out=128):
        super(RobertaCaptions, self).__init__()
        #self.roberta = torch.hub.load('pytorch/fairseq', 'roberta.large').cuda()
        self.features=nn.Sequential(nn.Linear(300, 1024, bias=True),
                                        nn.ReLU(inplace=True), nn.Dropout(0.5))
        self.classifier = nn.Sequential(nn.Linear(1024, 512, bias=True),
                                        nn.ReLU(inplace=True),
                                        nn.Dropout(0.5)).cuda()
        self.top_layer=nn.Linear(512, out).cuda()

        self._initialize_weights()

    def forward(self, x):
        #x = self.extract_features(x)
        x=self.features(x)
        x=self.classifier(x)
        if self.top_layer:
            x = self.top_layer(x)
        return x #self.pool(x.permute(0, 2, 1))  # .cuda()).detach().cpu()

    def extract_features(self, x):
        x=self.features(x)
        x=self.classifier(x)
        '''
        tokens = self.roberta.encode(x)
        tokens=tokens[:512]
        x = self.roberta.extract_features(tokens)
        pool= nn.AdaptiveAvgPool2d((1,1024)) #nn.MaxPool2d((x.shape[1], 1))
        x=pool(x).squeeze(1)
        '''
        return x
    def encode(self, x):

        return self.roberta.encode(x)

    def _initialize_weights(self):
        self.features[0].weight.data.normal_(0, 0.01)
        self.features[0].bias.data.zero_()
        self.classifier[0].weight.data.normal_(0, 0.01)
        self.classifier[0].bias.data.zero_()
        self.top_layer.weight.data.normal_(0, 0.01)
        self.top_layer.bias.data.zero_()

def roberta_model(sobel=False, bn=True, out=10):
    model = RobertaCaptions(out)
    return model

def grab_text(dictionary_path):
    model=roberta_model()
    i =0
    with open(dictionary_path, 'rb') as f:
        captions_df=pickle.load(f)
        for key, item in captions_df.items():
            tmp = ' '.join(list(item['text']))
            tmp=model.extract_features(tmp).squeeze(0)
            print(i, tmp.shape)
            with open('./embeddings/%s.pickle' %key, 'wb') as f:
                pickle.dump(tmp, f)
            i+=1
    return i

if __name__ == '__main__':
    import os
    dict_path=os.path.join('/home/crcvreu.student6/COIN_HowTo', 'coin_howto_overlap_captions.pickle')
    grab_text(dict_path)
