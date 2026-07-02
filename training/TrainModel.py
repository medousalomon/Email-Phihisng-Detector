import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Bidirectional



# LOAD DATA

X = np.load("../data/processed/features.npy")
y = np.load("../data/processed/labels.npy")

# ADDING CLASS WEIGHTS

from sklearn.utils import class_weight

class_weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y),
    y=y
)

class_weights = dict(enumerate(class_weights))

# TRAIN / TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)



# MODEL

model = Sequential([
    Embedding(input_dim=10000, output_dim=128, input_length=X.shape[1]),
    Bidirectional(LSTM(64, return_sequences=True)),
    LSTM(32),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])


model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=2,
    restore_best_weights=True
)

# TRAIN

print("Training model...")

model.fit(
    X_train,
    y_train,
    epochs=15,
    batch_size=64,
    validation_data=(X_test, y_test),
    class_weight=class_weights, # adding class weights to handle imbalance
    callbacks=[early_stop]
)


# EVALUATION

y_pred = (model.predict(X_test) > 0.5).astype("int32")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# SAVE MODEL

model.save("../models/phishing_model.h5")

print("Model saved!")