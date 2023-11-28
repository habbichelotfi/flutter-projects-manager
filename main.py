import os
import subprocess
from PyQt5.QtWidgets import QLabel, QListWidgetItem, QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QTextEdit, QMessageBox
import yaml  # pip install PyYAML


from PyQt5.QtGui import QColor


def display_dependencies():
    selected_project_index = projects_list.currentRow()
    if selected_project_index < 0:
        QMessageBox.information(window, "Info", "No project selected")
        return

    project_path = os.path.join(flutter_projects_path, projects_list.item(selected_project_index).text())
    pubspec_path = os.path.join(project_path, 'pubspec.yaml')
    
    try:
        with open(pubspec_path, 'r') as file:
            pubspec = yaml.safe_load(file)
            dependencies = pubspec.get('dependencies', {})
            dev_dependencies = pubspec.get('dev_dependencies', {})
            
            # Clear and update the dependencies list
            dependencies_list.clear()
            for dep in dependencies:
                dependencies_list.addItem(f"{dep} (version: {dependencies[dep]})")
            for dev_dep in dev_dependencies:
                dependencies_list.addItem(f"{dev_dep} (version: {dev_dependencies[dev_dep]})")
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Failed to read dependencies: {e}")



def find_flutter_projects(path):
    projects_list.clear()
    for root, dirs, files in os.walk(path):
        if 'pubspec.yaml' in files:
            project_name = os.path.basename(root)
            list_item = QListWidgetItem(project_name)
            if 'build' in dirs:  # Simple status check
                list_item.setBackground(QColor('yellow'))  # Change color to indicate status
            projects_list.addItem(list_item)

def run_flutter_clean():
    selected_projects_indices = [projects_list.row(i) for i in projects_list.selectedItems()]
    if not selected_projects_indices:
        QMessageBox.information(window, "Info", "No projects selected")
        return

    for project in selected_projects_indices:
        project_path = os.path.join(flutter_projects_path, projects_list.item(project).text())

        try:
            result = subprocess.run(["flutter", "clean"], cwd=project_path, capture_output=True, text=True)
            if result.returncode != 0:
                QMessageBox.critical(window, "Error", f"Failed to clean project {project_path}\n{result.stderr}")
            else:
                QMessageBox.information(window, "Success", f"Project cleaned: {project_path}")
        except subprocess.SubprocessError as e:
            QMessageBox.critical(window, "Subprocess Error", str(e))
        except Exception as e:
            QMessageBox.critical(window, "Error", f"An unexpected error occurred: {e}")

def filter_projects(text):
    for index in range(projects_list.count()):
        item = projects_list.item(index)
        item.setHidden(text.lower() not in item.text().lower())

app = QApplication([])
window = QWidget()
window.resize(1200, 1000)  # Width = 800, Height = 600

layout = QVBoxLayout()

search_bar = QLineEdit()
search_bar.setPlaceholderText("Search Projects...")
search_bar.textChanged.connect(filter_projects)
layout.addWidget(search_bar)


projects_list = QListWidget()
layout.addWidget(projects_list)


dependencies_label = QLabel("Dependencies:")
layout.addWidget(dependencies_label)

dependencies_list = QListWidget()
layout.addWidget(dependencies_list)

show_deps_button = QPushButton("Show Dependencies")
show_deps_button.clicked.connect(display_dependencies)
layout.addWidget(show_deps_button)

clean_button = QPushButton("Run Flutter Clean")
clean_button.clicked.connect(run_flutter_clean)
layout.addWidget(clean_button)

log_output = QTextEdit()
log_output.setReadOnly(True)
layout.addWidget(log_output)

window.setLayout(layout)
window.setWindowTitle("Flutter Project Manager")

flutter_projects_path="path/flutter/projects"
find_flutter_projects(flutter_projects_path)

window.show()
app.exec_()
