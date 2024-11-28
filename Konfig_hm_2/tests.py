import unittest
import os
from visualizer import parse_config, parse_pom, get_all_dependencies, build_graph, visualize_graph

class TestDependencyVisualizer(unittest.TestCase):

    def setUp(self):
        # Создаем временные файлы для тестов
        self.test_config = 'test_config.xml'
        with open(self.test_config, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<config>
    <graphviz_path>/usr/bin/dot</graphviz_path>
    <package_path>./test_package</package_path>
</config>''')

        self.test_pom = './test_package/pom.xml'
        os.makedirs('./test_package', exist_ok=True)
        with open(self.test_pom, 'w') as f:
            f.write('''<project xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
    https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>test-artifact</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.12</version>
        </dependency>
    </dependencies>
</project>''')

    def test_parse_config(self):
        """Тестирует функцию parse_config для корректного парсинга config.xml."""
        graphviz_path, package_path = parse_config('./test_config.xml')

        # Нормализуем пути с учётом текущей ОС
        if os.name == 'nt':  # Windows
            expected_graphviz_path = os.path.normpath('C:\\usr\\bin\\dot')
            expected_package_path = os.path.normpath('.\\test_package')
        else:  # Unix
            expected_graphviz_path = os.path.normpath('/usr/bin/dot')
            expected_package_path = os.path.normpath('./test_package')

        # Проверяем, что пути совпадают
        self.assertEqual(graphviz_path, os.path.abspath(expected_graphviz_path))
        self.assertEqual(package_path, os.path.abspath(expected_package_path))

    def test_parse_pom(self):
        dependencies = parse_pom(self.test_pom)
        self.assertEqual(len(dependencies), 1)
        self.assertEqual(dependencies[0]['group_id'], 'junit')
        self.assertEqual(dependencies[0]['artifact_id'], 'junit')
        self.assertEqual(dependencies[0]['version'], '4.12')

    def test_get_all_dependencies(self):
        # Для упрощения теста считаем, что нет транзитивных зависимостей
        dependencies = get_all_dependencies(self.test_pom)
        self.assertEqual(len(dependencies), 1)

    def test_build_graph(self):
        dependencies = [
            {
                'group_id': 'com.example',
                'artifact_id': 'test-artifact',
                'version': '1.0.0',
                'dependencies': [
                    {
                        'group_id': 'junit',
                        'artifact_id': 'junit',
                        'version': '4.12',
                        'dependencies': []
                    }
                ]
            }
        ]
        graph_lines = build_graph(dependencies)
        expected_lines = [
            'digraph G {',
            '"com.example:test-artifact" -> "junit:junit";'
        ]
        self.assertTrue(all(line in graph_lines for line in expected_lines))

    def tearDown(self):
        # Удаляем временные файлы после тестов
        os.remove(self.test_config)
        os.remove(self.test_pom)
        os.rmdir('./test_package')

if __name__ == '__main__':
    unittest.main()
