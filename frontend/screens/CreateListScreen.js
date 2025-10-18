import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import apiClient from '../api/client';

const CreateListScreen = ({ navigation }) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleParseList = async () => {
    if (!text.trim()) {
      Alert.alert('Error', 'Por favor, introduce tu lista de compras.');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/list/parse', { text_input: text });
      // Suponiendo que la respuesta es la lista de items.
      // Navegamos a la pantalla de la lista pasándole los datos.
      navigation.navigate('ShoppingList', { items: response.data });
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'No se pudo procesar la lista. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Ej: 2 leches, 1 café de 12990..."
        multiline
        value={text}
        onChangeText={setText}
      />
      {loading ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : (
        <Button title="Crear Mi Lista" onPress={handleParseList} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  input: {
    height: 150,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 20,
    padding: 10,
    textAlignVertical: 'top',
  },
});

export default CreateListScreen;