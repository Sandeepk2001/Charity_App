import pandas as pd
import numpy as np
import re
import string
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling1D, Embedding, MultiHeadAttention, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
import tensorflow as tf


df = pd.read_csv("train.csv", encoding='ISO-8859-1')


def preprocess_text(text):
    if isinstance(text, str):
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    elif isinstance(text, float):  
        text = str(text)  
    return text

df['text'] = df['text'].apply(preprocess_text)


# Tokenization and padding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['text'])
max_length = 100  
sequences = tokenizer.texts_to_sequences(df['text'])
X = pad_sequences(sequences, maxlen=max_length, padding='post')


# Label Encoding
label_encoder = LabelEncoder()
df['label'] = label_encoder.fit_transform(df['sentiment'])
y = df['label']


# Train-test split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)


# Model architecture
embedding_dim = 32  
num_heads = 2  
ff_dim = 32  
vocab_size = len(tokenizer.word_index) + 1

inputs = Input(shape=(max_length,))
embedding_layer = Embedding(vocab_size, embedding_dim)(inputs)
attention_output = MultiHeadAttention(num_heads=num_heads, key_dim=embedding_dim)(embedding_layer, embedding_layer)
attention_output = GlobalAveragePooling1D()(attention_output)
outputs = Dense(3, activation='softmax')(attention_output)

model = Model(inputs=inputs, outputs=outputs)
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val), 
          )

model.save("sentiment_model.h5")
np.save("tokenizer_word_index.npy", tokenizer.word_index)

# Save label encoder's classes
np.save("label_encoder_classes.npy", label_encoder.classes_)

loaded_model = tf.keras.models.load_model("sentiment_model.h5")


input_text = "Bad website"
preprocessed_text = preprocess_text(input_text)

# Tokenize and pad the preprocessed text
input_sequence = tokenizer.texts_to_sequences([preprocessed_text])
input_sequence_padded = pad_sequences(input_sequence, maxlen=max_length, padding='post')

# Make predictions
prediction = loaded_model.predict(input_sequence_padded)

# Convert prediction to class label
predicted_label = np.argmax(prediction)

# Convert label back to original sentiment label
predicted_sentiment = label_encoder.inverse_transform([predicted_label])[0]

print("Predicted sentiment:", predicted_sentiment)