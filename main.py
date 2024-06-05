from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from kivymd.uix.screenmanager import MDScreenManager  # Importe o MDScreenManager correto
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime


from google.cloud import firestore
from google.oauth2 import service_account
import pyrebase
import os

firebaseConfig = {
    "apiKey": "AIzaSyC-3voA9ZXvy87zus14c8gkQsnQCj9NX9M",
    "authDomain": "barbearia-e1e6c.firebaseapp.com",
    "databaseURL": "https://barbearia-e1e6c-default-rtdb.firebaseio.com",
    "projectId": "barbearia-e1e6c",
    "storageBucket": "barbearia-e1e6c.appspot.com",
    "messagingSenderId": "968526300490",
    "appId": "1:968526300490:web:94753b9f07e07209aaadb3",
    "measurementId": "G-LN9365N0QF"
}

precos_servicos = {
    "Corte social": 15.00,
    "Corte degrade": 20.00,
    "Corte tesoura": 15.00,
    "Barba na máquina": 20.00,
    "Cabelo + barba": 35.00,
    "Hidratação cabelo": 35.00,
    "Sombrancelha": 5.00,
    "Pigmentação": 15.00,
    "Hidratação barba": 25.00,
    "Acabamento": 7.50
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
credentials = service_account.Credentials.from_service_account_file('barberadmin.json')

# Inicialize Firestore
cred_path = "barberadmin.json"  # Caminho para o arquivo de chave de conta de serviço
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
firestore_client = firestore.Client()

class FirstScreen(MDScreen):
    pass

class LoginScreen(MDScreen):
    dialog = None


    def login_user(self):
        email = self.ids.login_email.text
        password = self.ids.login_password.text
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # Pegue o username do Firestore
            user_id = user['localId']
            user_ref = firestore_client.collection("users").document(user_id).get()
            username = user_ref.to_dict()["username"]
            self.manager.get_screen('tela principal').ids.username_label.text = f"Bem-vindo, {username}!"
            self.manager.current = 'tela principal'
        except Exception as e:
            self.show_error_dialog("Email ou senha incorretos")


    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()

    

class RegisterScreen(MDScreen):
    dialog = None

    def register_user(self):
        email = self.ids.email_field.text
        password = self.ids.password_field.text
        username = self.ids.username_field.text 
        telefone = self.ids.telefone_field.text 

        # Verificar se a senha tem pelo menos 6 caracteres
        if len(password) < 6:
            self.show_error_dialog("A senha deve ter pelo menos 6 caracteres.")
            return

        try:
            user = auth.create_user_with_email_and_password(email, password)
            
            # Salvar o nome de usuário, email e senha no Firestore
            user_id = user['localId']
            user_ref = firestore_client.collection("users").document(user_id)
            user_ref.set({
                "username": username,
                "email": email,
                "password": password,
                "telefone": telefone
            })
            
            self.manager.current = 'tela de login'
        except Exception as e:
            self.show_error_dialog(f"Erro ao criar usuário: {e}")

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()

class MainScreen(MDScreen):
    def logout(self):
        auth.current_user = None
        self.manager.current = 'tela de login'

class Localizacao(MDScreen):
    pass

class Agendamento(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicos_selecionados = []
        self.total_preco = 0.00  # Total inicial

    def dropdown_(self):
        self.menu_list = [
            {"viewclass": "OneLineListItem", "text": "Corte social", "on_release": lambda x="Corte social": self.test1(x)},
            {"viewclass": "OneLineListItem", "text": "Corte degrade", "on_release": lambda x="Corte degrade": self.test2(x)},
            {"viewclass": "OneLineListItem", "text": "Corte tesoura", "on_release": lambda x="Corte tesoura": self.test3(x)},
            {"viewclass": "OneLineListItem", "text": "Barba na máquina", "on_release": lambda x="Barba na máquina": self.test4(x)},
            {"viewclass": "OneLineListItem", "text": "Cabelo + barba", "on_release": lambda x="Cabelo + barba": self.test5(x)},
            {"viewclass": "OneLineListItem", "text": "Hidratação cabelo", "on_release": lambda x="Hidratação cabelo": self.test6(x)},
            {"viewclass": "OneLineListItem", "text": "Sombrancelha", "on_release": lambda x="Sombrancelha": self.test7(x)},
            {"viewclass": "OneLineListItem", "text": "Pigmentação", "on_release": lambda x="Pigmentação": self.test8(x)},
            {"viewclass": "OneLineListItem", "text": "Hidratação barba", "on_release": lambda x="Hidratação barba": self.test9(x)},
            {"viewclass": "OneLineListItem", "text": "Acabamento", "on_release": lambda x="Acabamento": self.test10(x)}
        ]

        self.menu = MDDropdownMenu(
            caller=self.ids.menu_,
            items=self.menu_list,
            width_mult=4
        )
        self.menu.open()

    def test1(self, service):
        self.select_service(service)

    def test2(self, service):
        self.select_service(service)

    def test3(self, service):
        self.select_service(service)

    def test4(self, service):
        self.select_service(service)

    def test5(self, service):
        self.select_service(service)

    def test6(self, service):
        self.select_service(service)

    def test7(self, service):
        self.select_service(service)

    def test8(self, service):
        self.select_service(service)

    def test9(self, service):
        self.select_service(service)

    def test10(self, service):
        self.select_service(service)

    def select_service(self, service):
        if len(self.servicos_selecionados) >= 5:
            self.show_error_dialog("Você pode adicionar no máximo 5 serviços.")
            return

        if service in self.servicos_selecionados:
            self.show_error_dialog("Você já selecionou este serviço.")
            return

        self.servicos_selecionados.append(service)
        self.total_preco += precos_servicos[service]
        print(f"{service} adicionado com sucesso!")
        self.show_success_dialog(f"{service} adicionado com sucesso!")
        self.ids.preco_label.text = f"Total: R$ {self.total_preco:.2f}"
        self.ids.menu_.text = service
        self.menu.dismiss()

    def remover_servico(self):
        if not self.servicos_selecionados:
            self.show_error_dialog("Nenhum serviço para remover.")
            return

    # Remover o último serviço adicionado
        ultimo_servico = self.servicos_selecionados.pop()
        self.total_preco -= precos_servicos[ultimo_servico]
        print(f"{ultimo_servico} removido com sucesso!")
        self.show_success_dialog(f"{ultimo_servico} removido com sucesso!")
        self.ids.preco_label.text = f"Total: R$ {self.total_preco:.2f}"
        self.ids.menu_.text = "Serviços"  # Resetar o texto do botão para "Serviços"


    def agendar(self):
        if not self.servicos_selecionados:
            self.show_error_dialog("Por favor, selecione pelo menos um serviço.")
            return

        data_agendamento = self.ids.data_field.text

        # Verificar se a data inserida é válida (formato dd/mm/aaaa)
        try:
            data = datetime.strptime(data_agendamento, "%d/%m/%Y")
        except ValueError:
            self.show_error_dialog("Formato de data inválido. Insira uma data no formato dd/mm/aaaa.")
            return

        # Verificar se a data inserida é maior ou igual à data atual
        if data.date() < datetime.now().date():
            self.show_error_dialog("Coloque uma data certa.")
            return

        try:
            user_id = auth.current_user["localId"]
            agendamento_ref = firestore_client.collection("agendamentos").document(user_id)
            agendamento_ref.set({
                "servicos": self.servicos_selecionados,
                "data": data_agendamento,
                "total_preco": self.total_preco
            })

            self.show_success_dialog("Agendamento realizado com sucesso!")
        except Exception as e:
            self.show_error_dialog(f"Erro ao agendar: {e}")

    def show_success_dialog(self, message):
        dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

    def show_error_dialog(self, message):
        dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
class Barbeiros(MDScreen):
    pass

class Servicos(MDScreen):
    pass

class MyApp(MDApp):
    
    def build(self):
        Window.size = (dp(360), dp(640))
        Builder.load_file('main.kv')  # Certifique-se de que o arquivo main.kv esteja no mesmo diretório
        self.theme_cls.primary_palette = 'Gray'
        self.theme_cls.theme_style = "Dark"
        screens = MDScreenManager()
        screens.add_widget(FirstScreen())
        screens.add_widget(LoginScreen())
        screens.add_widget(RegisterScreen())
        screens.add_widget(MainScreen())
        screens.add_widget(Localizacao())
        screens.add_widget(Agendamento())
        screens.add_widget(Barbeiros())
        screens.add_widget(Servicos())
        return screens
    

    

if __name__ == '__main__':
    MyApp().run()
