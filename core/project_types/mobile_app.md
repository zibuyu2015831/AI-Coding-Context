---
title: 移动应用项目配置
summary: 定义移动应用项目（React Native/Flutter/原生开发）的推荐子文档清单、特殊关注点和核心代码模式。包括平台特定代码、导航结构、原生模块等关键规范。
keywords: mobile-app | react-native | flutter | ios | android | native | navigation
scope: 移动应用项目类型配置
related_files: 无
dependencies: core/project_types.md
verified_at: 2026-01-21
---

# 移动应用项目

> **适用框架**: React Native / Flutter / Ionic / NativeScript / 原生开发

---

## 🎯 适用框架

### 跨平台
- **React Native**: JavaScript/TypeScript，React 生态
- **Flutter**: Dart，高性能 UI
- **Ionic**: Web 技术，Capacitor/Cordova
- **NativeScript**: JavaScript/TypeScript，原生 API

### 原生
- **iOS**: SwiftUI / UIKit
- **Android**: Jetpack Compose / XML Views

---

## 📋 推荐子文档清单

| 优先级 | 文档名称 | 用途 |
|-------|---------|------|
| 🔴 高 | `platform_specific.md` | 平台特定代码 |
| 🔴 高 | `navigation.md` | 导航结构 |
| 🔴 高 | `native_modules.md` | 原生模块 |
| 🟡 中 | `state_management.md` | 状态管理 |
| 🟡 中 | `build_release.md` | 构建与发布 |
| 🟡 中 | `testing_guide.md` | 测试策略 |

---

## 🔍 特殊关注点

### 原生依赖管理

- **iOS**: CocoaPods / Swift Package Manager
- **Android**: Gradle dependencies

### 热更新方案

- **CodePush**: React Native 热更新
- **Shorebird**: Flutter 热更新

### 性能优化

- **列表渲染**: FlatList / RecyclerView / ListView
- **图片优化**: 缓存、懒加载、压缩
- **内存管理**: 避免内存泄漏

### 平台差异处理

- **Platform API**: 检测平台
- **条件编译**: 平台特定代码
- **UI 适配**: 不同屏幕尺寸和密度

### 打包签名配置

- **iOS**: Provisioning Profile / Certificate
- **Android**: Keystore / Signing Config

---

## 💻 核心代码模式

### React Native 项目结构

```typescript
// App.tsx
import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import HomeScreen from './screens/HomeScreen'
import DetailsScreen from './screens/DetailsScreen'

const Stack = createNativeStackNavigator()

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  )
}

// screens/HomeScreen.tsx
import React from 'react'
import { View, Text, Button, StyleSheet, Platform } from 'react-native'

export default function HomeScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Home Screen</Text>
      <Button
        title="Go to Details"
        onPress={() => navigation.navigate('Details')}
      />
      {Platform.OS === 'ios' && (
        <Text>iOS specific content</Text>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20
  }
})
```

### 平台特定代码

```typescript
// Platform.select
import { Platform, StyleSheet } from 'react-native'

const styles = StyleSheet.create({
  container: {
    ...Platform.select({
      ios: {
        backgroundColor: '#f0f0f0'
      },
      android: {
        backgroundColor: '#ffffff'
      }
    })
  }
})

// 平台特定文件
// Button.ios.tsx
export default function Button() {
  return <IOSButton />
}

// Button.android.tsx
export default function Button() {
  return <AndroidButton />
}
```

### 原生模块调用

```typescript
// 调用原生模块
import { NativeModules } from 'react-native'

const { CalendarModule } = NativeModules

// 调用原生方法
CalendarModule.createEvent('Party', '2024-01-01')
  .then(eventId => {
    console.log(`Created event with id ${eventId}`)
  })
  .catch(error => {
    console.error(error)
  })
```

### Flutter 项目结构

```dart
// main.dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomeScreen(),
    );
  }
}

// screens/home_screen.dart
class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home Screen'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Counter:',
              style: Theme.of(context).textTheme.headline6,
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headline4,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),
    );
  }
}
```

### 状态管理（Redux）

```typescript
// store/store.ts
import { configureStore } from '@reduxjs/toolkit'
import userReducer from './userSlice'

export const store = configureStore({
  reducer: {
    user: userReducer
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// store/userSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UserState {
  name: string
  email: string
}

const initialState: UserState = {
  name: '',
  email: ''
}

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<UserState>) => {
      state.name = action.payload.name
      state.email = action.payload.email
    }
  }
})

export const { setUser } = userSlice.actions
export default userSlice.reducer

// 在组件中使用
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from './store/store'
import { setUser } from './store/userSlice'

function ProfileScreen() {
  const user = useSelector((state: RootState) => state.user)
  const dispatch = useDispatch()

  const updateUser = () => {
    dispatch(setUser({ name: 'John', email: 'john@example.com' }))
  }

  return (
    <View>
      <Text>{user.name}</Text>
      <Button title="Update" onPress={updateUser} />
    </View>
  )
}
```

### 性能优化

```typescript
// 使用 React.memo 避免不必要的重渲染
const ListItem = React.memo(({ item }) => {
  return (
    <View>
      <Text>{item.title}</Text>
    </View>
  )
})

// 使用 FlatList 渲染大列表
import { FlatList } from 'react-native'

function MyList({ data }) {
  return (
    <FlatList
      data={data}
      renderItem={({ item }) => <ListItem item={item} />}
      keyExtractor={item => item.id}
      initialNumToRender={10}
      maxToRenderPerBatch={10}
      windowSize={5}
      removeClippedSubviews={true}
    />
  )
}

// 图片优化
import FastImage from 'react-native-fast-image'

function ImageComponent({ uri }) {
  return (
    <FastImage
      source={{ uri, priority: FastImage.priority.normal }}
      style={{ width: 200, height: 200 }}
      resizeMode={FastImage.resizeMode.cover}
    />
  )
}
```

---

## ⚠️ 常见问题

### 问题 1: 原生依赖安装失败

**解决方案**: 清理并重新安装

```bash
# React Native
cd ios && pod install && cd ..
# 或清理后重装
cd ios && pod deintegrate && pod install && cd ..

# Android
cd android && ./gradlew clean && cd ..
```

### 问题 2: 性能问题

**解决方案**: 使用性能分析工具

```typescript
// React Native Performance Monitor
import { PerformanceObserver } from 'react-native'

const observer = new PerformanceObserver((list) => {
  const entries = list.getEntries()
  entries.forEach((entry) => {
    console.log(`${entry.name}: ${entry.duration}ms`)
  })
})

observer.observe({ entryTypes: ['measure'] })
```

### 问题 3: 平台差异导致的 Bug

**解决方案**: 使用平台检测和条件渲染

```typescript
import { Platform } from 'react-native'

// 方法1: Platform.OS
if (Platform.OS === 'ios') {
  // iOS specific code
}

// 方法2: Platform.select
const styles = Platform.select({
  ios: { paddingTop: 20 },
  android: { paddingTop: 0 }
})
```

---

## 🎯 检查清单

生成移动应用项目文档前，确认：

- [ ] 已识别主要框架（React Native/Flutter/原生）
- [ ] 已确定目标平台（iOS/Android/Both）
- [ ] 已确定导航方案（React Navigation/Flutter Navigator）
- [ ] 已确定状态管理方案（Redux/MobX/Provider）
- [ ] 已确定是否需要原生模块
- [ ] 已确定图片和资源管理策略
- [ ] 已确定构建和发布流程
- [ ] 已确定测试策略（单元/集成/E2E）
- [ ] 已确定是否需要热更新

---

**版本**: v3.0  
**路径**: `core/project_types/mobile_app.md`  
**最后更新**: 2026-01-21
