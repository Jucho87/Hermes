import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import CreateListScreen from '../screens/CreateListScreen';
import ShoppingListScreen from '../screens/ShoppingListScreen';
import ReportsScreen from '../screens/ReportsScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="CreateList">
        <Stack.Screen
          name="CreateList"
          component={CreateListScreen}
          options={{ title: 'Crear Nueva Lista' }}
        />
import { Button } from 'react-native';

// ... (resto de las importaciones)

// ... (código del StackNavigator)

// ...

        <Stack.Screen
          name="ShoppingList"
          component={ShoppingListScreen}
          options={({ navigation }) => ({
            title: 'Mi Lista de Compras',
            headerRight: () => (
              <Button
                onPress={() => navigation.navigate('Reports')}
                title="Reportes"
                color="#007AFF"
              />
            ),
          })}
        />
        <Stack.Screen
          name="Reports"
          component={ReportsScreen}
          options={{ title: 'Reportes de Gastos' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;