import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert, Button } from 'react-native';
import apiClient from '../api/client';

const ReportsScreen = ({ navigation }) => {
  const [comparison, setComparison] = useState(null);
  const [byCategory, setByCategory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const comparisonPromise = apiClient.get('/report/spending-comparison');
      const byCategoryPromise = apiClient.get('/report/spending-by-category');

      const [comparisonResponse, byCategoryResponse] = await Promise.all([
        comparisonPromise,
        byCategoryPromise,
      ]);

      setComparison(comparisonResponse.data);
      setByCategory(byCategoryResponse.data);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'No se pudieron cargar los reportes.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Escuchar el evento 'focus' para recargar los datos cada vez que se visita la pantalla
    const unsubscribe = navigation.addListener('focus', fetchReports);
    return unsubscribe;
  }, [navigation]);

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" style={styles.loader} />;
  }

  return (
    <View style={styles.container}>
      {comparison && (
        <View style={styles.card}>
          <Text style={styles.title}>Gasto Comparativo</Text>
          <Text>Total Estimado: ${comparison.total_estimated.toFixed(2)}</Text>
          <Text>Total Real: ${comparison.total_real.toFixed(2)}</Text>
          <Text style={{ color: comparison.variation_percentage > 0 ? 'red' : 'green' }}>
            Variación: {comparison.variation_percentage.toFixed(2)}%
          </Text>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.title}>Gasto por Categoría</Text>
        {byCategory.length > 0 ? (
          byCategory.map((cat, index) => (
            <Text key={index}>- {cat.category}: ${cat.total_spent.toFixed(2)}</Text>
          ))
        ) : (
          <Text>No hay datos de gasto por categoría.</Text>
        )}
      </View>

      <Button title="Recargar Reportes" onPress={fetchReports} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f5f5f5',
  },
  loader: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
});

export default ReportsScreen;