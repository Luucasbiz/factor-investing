from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from time import sleep
import MetaTrader5 as mt5
import logging
import datetime

# Volume das ordens pode ser configurado diretamente aqui 
VOLUME_DA_ORDEM = 500.0 

class InvestmentManager: 
    def __init__(self, url="https://www.fundamentus.com.br/resultado.php", login=None, password=None, server=None, volume=VOLUME_DA_ORDEM):
        """Inicializa a classe com a URL alvo, credenciais do MetaTrader 5 e volume das ordens."""
        self.url = url
        self.driver = None
        self.tabela = None
        self.tickers = None
        self.login = login
        self.password = password
        self.server = server
        self.volume = volume 

    def iniciar_navegador_chrome(self):
        """Inicializa o WebDriver do Chrome."""
        logging.info("Inicializando o WebDriver...")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def extrair_dados(self):
        """Realiza o scraping, limpa e filtra os dados, e seleciona os 10 melhores tickers."""
        try:
            # Inicializa o driver e acessa a URL
            self.iniciar_navegador_chrome() 
            logging.info("Acessando a página do Fundamentus...")
            self.driver.get(self.url)

            # Espera até que a tabela seja carregada
            local_tabela = '/html/body/div[1]/div[2]/table'
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, local_tabela)))

            # Extrai a tabela
            elemento = self.driver.find_element(By.XPATH, local_tabela)
            html_tabela = elemento.get_attribute("outerHTML")
            self.tabela = pd.read_html(str(html_tabela), thousands="-")[0]

            # Limpeza dos dados
            self.tabela = self.tabela.set_index("Papel")
            for col in self.tabela.columns:
                self.tabela[col] = self.tabela[col].str.replace("%", "", regex=False)
                self.tabela[col] = self.tabela[col].str.replace(".", "", regex=False)
                self.tabela[col] = self.tabela[col].str.replace(",", "", regex=False)
                self.tabela[col] = self.tabela[col].astype(float)

            # Filtros e rankings
            self.tabela = self.tabela[["Cotação", "EV/EBIT", "ROIC", "Liq.2meses"]]
            self.tabela = self.tabela[self.tabela["Liq.2meses"] > 1_000_000]
            self.tabela = self.tabela[self.tabela["EV/EBIT"] > 0]
            self.tabela = self.tabela[self.tabela["ROIC"] > 0]

            self.tabela["ranking_ev_ebit"] = self.tabela["EV/EBIT"].rank(ascending=True)
            self.tabela["ranking_roic"] = self.tabela["ROIC"].rank(ascending=False)
            self.tabela["ranking_total"] = self.tabela["ranking_ev_ebit"] + self.tabela["ranking_roic"]

            # Seleciona os 10 melhores tickers
            self.tabela = self.tabela.sort_values("ranking_total")
            self.tabela = self.tabela.head(10)
            self.tickers = self.tabela.index.tolist()

            logging.info("Dados coletados com sucesso!")
            return self.tabela

        except Exception as e:
            logging.error(f"Erro ao coletar dados: {e}")
        finally:
            if self.driver:
                self.driver.quit()

    def exibir_tickers(self):
        """Exibe os tickers selecionados em uma lista.""" 
        if self.tickers: 
            tickers_str = ", ".join(self.tickers)
            logging.info(f"Tickers selecionados: ({tickers_str})")
        else:
            logging.warning("Nenhum ticker selecionado.") 

    def verificar_horario_mercado(self):
        """Verifica se o mercado de ações está aberto.""" 
        horario_abertura = datetime.time(10, 0, 0)
        horario_fechamento = datetime.time(18, 00, 0)
        horario_atual = datetime.datetime.now().time()

        if horario_abertura <= horario_atual <= horario_fechamento: 
            return True 
        return False 

    def validar_credenciais(self):
        """Verifica se as credenciais do MetaTrader 5 estão completas.""" 
        if not self.login or not self.password or not self.server:
            if not self.login:
                logging.error("Credencial de login não fornecida!")
            if not self.password:
                logging.error("Credencial de senha não fornecida!")
            if not self.server:
                logging.error("Credencial de servidor não fornecida!")
            return False
        logging.info("As credenciais foram validadas com êxito.") 
        return True

    def inicializar_mt5(self):
        """Inicializa a conexão com o MetaTrader 5.""" 
        logging.info("Verificando o horário do mercado...")

        # Verifica o horário do mercado antes de continuar
        if not self.verificar_horario_mercado():
            logging.warning("O mercado está fechado. Não será possível realizar a conexão com o MetaTrader 5 neste momento.") 
            return False

        logging.info("O mercado está aberto. Verificando as credenciais para conectar ao MetaTrader 5.") 

        # Verifica as credenciais antes de tentar a conexão
        if not self.validar_credenciais():
            logging.error("Credenciais do MetaTrader 5 não fornecidas ou incompletas!")
            return False 

        try:
            if not mt5.initialize(login=self.login, password=self.password, server=self.server):
                logging.error("Falha ao conectar com MetaTrader 5. Verifique suas credenciais.")
                return False
            logging.info("Conexão com o MetaTrader 5 estabelecida com sucesso!")
            return True
        except Exception as e:
            logging.error(f"Erro ao conectar com MetaTrader 5: {e}")
            return False 

    def exibir_termos_responsabilidade(self):
        """Exibe os termos de responsabilidade e captura a resposta do usuário.""" 
        print("\n### TERMO DE RESPONSABILIDADE ###")
        print("Este sistema é apenas para fins educacionais.")
        print("1 - Concordo\n2 - Não concordo")
        resposta = input("Digite sua opção: ")

        if resposta == "1":
            logging.info("Usuário concordou com os termos de responsabilidade.")
            return True
        if resposta == "2":
            logging.info("Usuário não concordou com os termos de responsabilidade.")
            return False
        logging.warning("Opção inválida fornecida pelo usuário.")
        return False

    def executar_ordens_compra(self):
        """Envia ordens de compra no MetaTrader 5.""" 
        if not self.tickers:
            logging.warning("Nenhum ticker disponível para envio de ordens.")
            return 

        # Solicita o termo de responsabilidade
        if not self.exibir_termos_responsabilidade():
            logging.info("Processo de envio de ordens abortado pelo usuário.")
            return

        logging.info("Enviando ordens...")
        for ticker in self.tickers:
            try:
                mt5.symbol_select(ticker)
                info = mt5.symbol_info(ticker)
                if not info or info.ask <= 0:
                    logging.warning(f"Dados inválidos para {ticker}.")
                    continue

                ordem_compra = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": ticker,
                    "volume": self.volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": info.ask,
                    "magic": 1,
                    "comment": "InvestmentManager",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_RETURN,
                }
                resultado = mt5.order_send(ordem_compra)

                # Verificação de erro ao enviar a ordem
                if resultado is not None and resultado.retcode == mt5.TRADE_RETCODE_DONE:
                    logging.info(f"Ordem de compra realizada para o ticker: {ticker} | Preço: {info.ask:.2f} | Volume: {self.volume:.2f}") 
                elif resultado is not None:
                    logging.error(f"Erro ao enviar ordem para {ticker}: {resultado.retcode}") 
                else:
                    logging.error(f"Erro ao enviar ordem para {ticker}: {mt5.last_error()}") 
 
            except Exception as e:
                logging.error(f"Erro ao enviar ordem para {ticker}: {e}") 

    def encerrar_mt5(self):
        """Encerra a conexão com o MetaTrader 5.""" 
        mt5.shutdown()
        logging.info("Conexão com o MetaTrader 5 encerrada.") 

if __name__ == "__main__": 
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Neste projeto, optei por não utilizar variáveis de ambiente. 
    LOGIN = ""  
    PASSWORD = "" 
    SERVER = "" 

    portfolio = InvestmentManager(login=LOGIN, password=PASSWORD, server=SERVER, volume=VOLUME_DA_ORDEM) 
    tabela_top10 = portfolio.extrair_dados()
    portfolio.exibir_tickers()

    if portfolio.inicializar_mt5():
        portfolio.executar_ordens_compra()
        portfolio.encerrar_mt5() 