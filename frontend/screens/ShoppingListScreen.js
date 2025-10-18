import React, { useState } from 'react';
import { View, Text, FlatList, Button, StyleSheet, Modal, TextInput, Alert } from 'react-native';
import apiClient from '../api/client';

const ShoppingListScreen = ({ route, navigation }) => {
  const { items: initialItems } = route.params;
  const [items, setItems] = useState(initialItems);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [realPrice, setRealPrice] = useState('');
  const [realQuantity, setRealQuantity] = useState('');

  const openPurchaseModal = (item) => {
    setSelectedItem(item);
    setRealPrice(item.estimated_price ? item.estimated_price.toString() : '');
    setRealQuantity(item.planned_quantity.toString());
    setModalVisible(true);
  };

  const handleMarkAsPurchased = async () => {
    if (!selectedItem || !realPrice || !realQuantity) {
      Alert.alert('Error', 'Por favor, completa todos los campos.');
      return;
    }

    try {
      await apiClient.post('/transaction/add', {
        shopping_list_item_id: selectedItem.id,
        real_unit_price: parseFloat(realPrice),
        real_quantity: parseFloat(realQuantity),
      });

      // Actualizar el estado del item en la lista
      setItems(prevItems =>
        prevItems.map(item =>
          item.id === selectedItem.id ? { ...item, status: 'purchased' } : item
        )
      );

      setModalVisible(false);
      Alert.alert('Éxito', `${selectedItem.item.name_standard} marcado como comprado.`);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'No se pudo marcar el artículo como comprado.');
    }
  };

  const handleUploadInvoice = async () => {
    // En una app real, usarías ImagePicker.launchImageLibraryAsync() de expo-image-picker
    Alert.alert(
      "Subir Factura (Simulado)",
      "En una aplicación real, esto abriría la galería de imágenes. Ahora, simularemos la llamada a la API.",
      [{ text: "OK", onPress: async () => {
        try {
          // Simulamos la subida de un archivo. El backend ya simula la respuesta del OCR.
          const formData = new FormData();
          formData.append('invoice_image', {
            uri: 'file:///dummy-path/invoice.jpg', // URI de archivo simulado
            name: 'invoice.jpg',
            type: 'image/jpeg',
          });

          // Suponemos que el ID de la lista es el del primer item
          const shoppingListId = items[0]?.id || 0;

          const response = await apiClient.post(`/invoice/ocr?shopping_list_id=${shoppingListId}`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          const { discrepancies } = response.data;
          if (discrepancies.length > 0) {
            let alertMessage = 'Se encontraron discrepancias:\n';
            discrepancies.forEach(d => {
              alertMessage += `\n- ${d.item_name_manual}: Manual $${d.price_manual}, Factura $${d.price_ocr}`;
            });
            Alert.alert("Discrepancias Encontradas", alertMessage);
          } else {
            Alert.alert("Éxito", "No se encontraron discrepancias en la factura.");
          }
        } catch (error) {
          console.error(error);
          Alert.alert("Error", "No se pudo procesar la factura.");
        }
      }}]
    );
  };

  const renderItem = ({ item }) => (
    <View style={styles.itemContainer}>
      <View style={styles.itemInfo}>
        <Text style={styles.itemName}>{item.item.name_standard}</Text>
        <Text>Cantidad Planeada: {item.planned_quantity}</Text>
        <Text>Precio Estimado: ${item.estimated_price || 'N/A'}</Text>
      </View>
      <Button
        title={item.status === 'purchased' ? 'Comprado' : 'Marcar'}
        onPress={() => openPurchaseModal(item)}
        disabled={item.status === 'purchased'}
      />
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={items}
        renderItem={renderItem}
        keyExtractor={item => item.id.toString()}
      />
      <Button title="Subir Factura (OCR)" onPress={handleUploadInvoice} />

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.centeredView}>
          <View style={styles.modalView}>
            <Text style={styles.modalText}>Confirmar Compra de {selectedItem?.item.name_standard}</Text>
            <TextInput
              style={styles.input}
              placeholder="Precio Real por Unidad"
              keyboardType="numeric"
              value={realPrice}
              onChangeText={setRealPrice}
            />
            <TextInput
              style={styles.input}
              placeholder="Cantidad Real Comprada"
              keyboardType="numeric"
              value={realQuantity}
              onChangeText={setRealQuantity}
            />
            <Button title="Confirmar Compra" onPress={handleMarkAsPurchased} />
            <Button title="Cancelar" onPress={() => setModalVisible(false)} color="red" />
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10 },
  itemContainer: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 15, borderBottomWidth: 1, borderBottomColor: '#ccc' },
  itemInfo: { flex: 1 },
  itemName: { fontWeight: 'bold', fontSize: 16 },
  centeredView: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' },
  modalView: { width: '80%', backgroundColor: 'white', borderRadius: 20, padding: 35, alignItems: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.25, shadowRadius: 4, elevation: 5 },
  modalText: { marginBottom: 15, textAlign: 'center', fontWeight: 'bold' },
  input: { height: 40, width: '100%', borderColor: 'gray', borderWidth: 1, marginBottom: 20, padding: 10 },
});

export default ShoppingListScreen;