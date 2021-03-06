import argparse
import caffe
import cv2
import numpy as np
import os

class FaceFeatureExtractor():
    def __init__(self, in_shape = (112, 112, 3), mean = 127.5, raw_scale = 128.0):
        prepath    = os.path.abspath(__file__)
        prepath    = os.path.dirname(prepath)
        prototxt   = prepath + '/model/model.prototxt'
        caffemodel = prepath + '/model/model-r50-am.caffemodel'
	caffe.set_mode_gpu()
        caffe.set_device(0)

        self.blob_name = 'pre_fc1'
        self.in_w      = in_shape[0]
        self.in_h      = in_shape[1]
        self.in_c      = in_shape[2]
        self.net       = caffe.Net(prototxt, caffemodel, caffe.TEST)
        self.mean      = mean
        self.mul       = 1.0/raw_scale

        self.net.blobs['data'].reshape(1, self.in_c, self.in_h, self.in_w) #reshap input blob to match img

    def input_norm(self, blob):
        blob = cv2.resize(blob, (self.in_w, self.in_h))
        blob = cv2.cvtColor(blob, cv2.COLOR_BGR2RGB)
        blob = blob.transpose(2, 0, 1)
        blob = blob.astype(np.float32)
        blob -= self.mean
        blob *= self.mul

        return blob

    def forward(self, blob):
        self.net.blobs['data'].data[0,:,:,:] = blob
        out = self.net.forward()

        out_shape  = out[self.blob_name].shape
        len_out    = 1
        for i in out_shape:
            len_out *= i

        return out[self.blob_name].reshape(len_out)

    def output_norm(self, blob):
        dist = 0
        for i in blob:
            dist += i**2
        dist = np.sqrt(dist)

        out_norm =  blob / dist
        return out_norm

    def extract_feature(self, img):
        blob = self.input_norm(img)
        out  = self.forward(blob)
        out  = self.output_norm(out)

        return out

    def get_dist(self, a, b):
        sqsum = (a - b) ** 2
        dist = 0
        for i in sqsum:
            dist += i
        return np.sqrt(dist)
        
       
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img1', '-i1', required=True, help='img path')
    parser.add_argument('--img2', '-i2', required=True, help='img path')
    args = parser.parse_args()

    ftr_extor = FaceFeatureExtractor()

    img1 = cv2.imread(args.img1)
    out1 = ftr_extor.extract_feature(img1)

    img2 = cv2.imread(args.img2)
    out2 = ftr_extor.extract_feature(img2)

    dist = ftr_extor.get_dist(out1, out2)

    print '\n\tThe distance between', args.img1, 'and', args.img2, 'is', dist

    
