

import csv
import matplotlib.pylab as plt
import numpy as np

#Load Udacity Data file driving_log.csv
filepath1 = 'udacity_data/driving_log.csv'

udacity_data = []
my_data = []

with open(filepath1) as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        udacity_data.append(line)

#Remove first line as it containts non values (Just titles)
udacity_data = udacity_data[1:]

#Load additional driving data called sharp_turn, there were arounf 2009 images
# This additional data set (recovery data) was NOT generated by me and was obtained from the below link 
# https://medium.com/@somnath.banerjee/behavioral-cloning-project-of-self-driving-car-nano-degree-9381aaa4da13#.5aji82ot2
filepath2 = 'sharp_turn/sharp_turn.csv'
with open(filepath2) as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        my_data.append(line)

#Remove First line as it containts non values (Just titles)
my_data = my_data[1:]

#Combine the Udacity data and recovery data, and new data is created
data = udacity_data + my_data

print('Udacity Data :',len(udacity_data))
print('My Data :',len(my_data))
print('Combined Data :',len(data))




from sklearn.model_selection import train_test_split
train_samples, validation_samples = train_test_split(data, test_size=0.05)

print('Training Set Samples:',len(train_samples))
print('Validation Set Samples:',len(validation_samples))




from sklearn.utils import shuffle
import matplotlib.image as mpimg

# Generator fucntion: I have refered udacity notes
def generator(samples, batch_size):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            for batch_sample in batch_samples:
                # Udacity images and additional Recovery images were put together in a new folder 'combined_data/IMG'
                name = './data/combined_data/IMG/'+batch_sample[0].split('/')[-1]
                center_image = mpimg.imread(name)
                center_angle = float(batch_sample[3])
                images.append(center_image)
                angles.append(center_angle)

            X_train = np.array(images)
            y_train = np.array(angles)
                        
            yield shuffle(X_train, y_train)

train_generator = generator(train_samples, batch_size=128)
validation_generator = generator(validation_samples, batch_size=128)




from keras.models import Sequential
from keras.layers.core import Dense, Activation, Flatten, Dropout, Lambda
from keras.layers import Conv2D, MaxPooling2D, Cropping2D
from keras.optimizers import Adam

#Nvidia Model was used with first two layers for preprocessing the images (Normalization and cropping) 
#https://devblogs.nvidia.com/parallelforall/deep-learning-self-driving-cars/
model = Sequential()

#Image normalization lambda layer
model.add(Lambda(lambda x: (x / 255.0) - 0.5, input_shape=(160,320,3)))
#Cropping layer: 70 pixels from the top of the image and 25 from the bottom
model.add(Cropping2D(cropping=((70, 25), (0, 0))))
# Convolutional layers similar to Nvidia Model
model.add(Convolution2D(24, 5, 5, subsample=(2, 2), activation='relu'))
model.add(Convolution2D(36, 5, 5, subsample=(2, 2), activation='relu'))
model.add(Convolution2D(48, 5, 5, subsample=(2, 2), activation='relu'))
model.add(Convolution2D(64, 3, 3, activation='relu'))
model.add(Convolution2D(64, 3, 3, activation='relu'))
model.add(Flatten())
#4 fully connected layers with dropout layers (KeepProb is set to 0.5)
model.add(Dropout(0.5))
model.add(Dense(1164, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(100, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(50, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(1, activation='tanh'))

#adam optimizer with default parameters
model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
model.summary()




nb_epoch = 2

# Train and save the model as 'model.h5', whiche will be help in drive.py 
model.fit_generator(train_generator, 
                    samples_per_epoch=len(train_samples), 
                    validation_data=validation_generator,
                    nb_val_samples=len(validation_samples), nb_epoch=nb_epoch)

model.save('model.h5')


