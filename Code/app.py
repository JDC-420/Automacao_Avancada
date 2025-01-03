import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

# Função para mostrar a interface e capturar os dados do utilizador
def show_interface():
    st.title("Cálculos de Eficiência Solar")

    # Perguntar ao utilizador qual opção escolher
    option = st.radio(
        "Escolha uma opção",
        ("Calcular com base em dados já obtidos", "Calcular com valores teóricos")
    )

    if option == "Calcular com valores teóricos":
        st.header("Cálculos com Valores Teóricos")

        # Solicitar o número de painéis solares
        num_panels = st.number_input(
            "Insira o número de painéis solares:",
            min_value=1, 
            step=1
        )

        # Solicitar a área útil de cada painel em metros quadrados
        panel_area = st.number_input(
            "Insira a área útil de cada painel (m²):", 
            min_value=0.001, 
            format="%.3f", 
            step=0.05
        )

       
        # Solicitar a eficiência geral do sistema com tooltip
        efficiency = st.number_input(
            "Insira a eficiência geral do sistema (%):",
            min_value=0.0, 
            max_value=100.0, 
            format="%.2f", 
            step=0.1,
            help="A eficiência geral do sistema pode ser calculada pela eficiência dos painéis (geralmente entre 15 a 20%) multiplicada pela eficiência restante do sistema (geralmente cerca de 85-95%, devido a perdas nos inversores, perdas devido à temperatura, perdas nos cabos, sujeira, etc.), resultando numa eficiência geral tipicamente entre os 12,5% e os 20%."
        )

        # Exibir a explicação sobre a eficiência geral do sistema
        with st.expander("⚡️ Clique para mais informações sobre a eficiência do sistema"):
            st.markdown("""
                A eficiência geral do sistema pode ser calculada pela eficiência dos painéis 
                (geralmente entre 15 a 20%) multiplicada pela eficiência restante do sistema 
                (geralmente cerca de 85-95%, devido a perdas nos inversores, perdas devido 
                à temperatura, perdas nos cabos, sujeira, etc.), resultando numa eficiência 
                geral tipicamente entre os 12,5% e os 20%.
            """)

        # Upload do arquivo de valores de irradiância
        st.subheader("Faça o upload do arquivo CSV com valores de irradiância")
         # Exibir a explicação sobre a eficiência geral do sistema
        with st.expander("⚡️ Clique para mais informações sobre o arquivo"):
            st.markdown("""
                Este arquivo é obtido através do PHOTOVOLTAIC GEOGRAPHICAL
                INFORMATION SYSTEM (PGIS) (URL: https://re.jrc.ec.europa.eu/pvg_tools/en/#MR).
                Após acessar o link, deve escolher a opção "Hourly Data" e preencher os dados para a
                situação que deseja, colocando a sua localização exata e o intervalo de tempo que desejar.
                Após descarregar o arquivo no formato .csv, só tem que fazer o upload dos mesmo e o programa trata do
                resto.
            """)
        uploaded_irradiance_desired_data = st.file_uploader(
            "Upload dos valores de irradiância para a instalação desejada", 
            type="csv"
        )

        if uploaded_irradiance_desired_data is not None:
            try:
                # Processar o arquivo de irradiância do sol para a instalação desejada
                df_irradiance_desired = pd.read_csv(
                    uploaded_irradiance_desired_data, 
                    delimiter=",", 
                    skiprows=8,
                    low_memory=False,  # Desativa a leitura em partes para evitar warnings de tipo
                    dtype={'time': str}  # Garantir que 'time' é tratado como string
                )
                df_irradiance_desired = df_irradiance_desired.dropna()

                # Manter as colunas 'time' e 'G(i)'
                df_irradiance_desired = df_irradiance_desired[['time', 'G(i)']]

                # Garantir que os valores de 'G(i)' são convertidos corretamente para float
                df_irradiance_desired['G(i)'] = pd.to_numeric(df_irradiance_desired['G(i)'], errors='coerce')

                # Verificar se existem valores NaN após conversão
                df_irradiance_desired = df_irradiance_desired.dropna()

                # Cálculo do fator x
                x = (efficiency / 100) * num_panels * panel_area / 1000

                # Multiplicar todos os valores de G(i) pelo fator x
                df_irradiance_desired['kWh'] = df_irradiance_desired['G(i)'] * x

                # Soma de todos os valores de kWh
                total_kwh = df_irradiance_desired['kWh'].sum()

                # Extração do ano a partir da coluna 'time'
                df_irradiance_desired['Year'] = df_irradiance_desired['time'].str[:4]

                # Soma de kWh por ano
                yearly_kwh = df_irradiance_desired.groupby('Year')['kWh'].sum().reset_index()
                yearly_kwh.columns = ['Year', 'Total_kWh']  # Corrigir nome da coluna para 'Total_kWh'

                # Arredondar os valores finais para exibição
                total_kwh_rounded = round(total_kwh)
                yearly_kwh['Total_kWh'] = yearly_kwh['Total_kWh'].round().astype(int)

                # Exibir resultados
                st.subheader("Resultados Finais")
                st.write(f"**Soma Total de kWh:** {total_kwh_rounded} kWh")

                # Exibir soma por ano
                for _, row in yearly_kwh.iterrows():
                    year = row['Year']
                    kwh = row['Total_kWh']
                    st.write(f"**Ano {year}:** {kwh} kWh")

            except Exception as e:
                st.error("Erro ao processar o arquivo. Verifique o formato do CSV e tente novamente.")
                st.error(f"Detalhes do erro: {e}")

    if option == "Calcular com base em dados já obtidos":
        st.header("Informações do Sistema Existente")

        # Solicitar o número de painéis solares
        num_panels = st.number_input("Insira o número de painéis solares:", min_value=1, step=1)

        # Solicitar a área útil de cada painel em metros quadrados
        panel_area = st.number_input("Insira a área útil de cada painel (m²):", 
                                     min_value=0.001, 
                                     format="%.3f", 
                                     step=0.05)

        # Verificar se o valor da área dos painéis é válido
        if panel_area <= 0:
            st.error("A área dos painéis solares deve ser maior que 0.")
        
        # Upload dos arquivos de dados
        st.subheader("Faça o upload dos arquivos CSV")

        # Exibir a explicação sobre a eficiência geral do sistema
        with st.expander("⚡️ Clique para mais informações sobre os arquivos"):
            st.markdown("""
                O primeiro arquivo deve conter os dados da produção de kWh da
                sua instalação de hora em hora, em que a primeira coluna (date)
                representa a data no formato dd/mm/aaaa hh:mm e a segunda coluna
                (Produced Energy (kWh)) representa o valor de energia produzida
                em kWh, deve estar no formato .csv, separado por ";".
                Os restantes arquivos são obtidos através do PHOTOVOLTAIC GEOGRAPHICAL
                INFORMATION SYSTEM (PGIS) (URL: https://re.jrc.ec.europa.eu/pvg_tools/en/#MR).
                Após acessar o link, deve escolher a opção "Hourly data" e preencher os dados para a sua situação,
                colocando a sua localização exata e o mesmo intervalo de tempo que usou
                para os dados da produção sua instalação e descarregar o ficheiro no formato .csv. De seguida faz
                exatamente o mesmo, mas para a situação que deseja e só tem que fazer o upload dos arquivos que o
                programa trata do resto.
            """)

        uploaded_prod_data = st.file_uploader("Upload dos dados de produção da sua instalação", type="csv")
        uploaded_irradiance_data = st.file_uploader("Upload dos dados de irradiância do sol relativamente à sua instalação", type="csv")
        uploaded_irradiance_desired_data = st.file_uploader("Upload dos dados da irradiância do sol para a instalação desejada", type="csv")

        if uploaded_prod_data is not None:
            # Processar o arquivo de dados de produção, mantendo apenas as duas primeiras colunas
            df_prod = pd.read_csv(uploaded_prod_data, delimiter=";")
            df_prod = df_prod.iloc[:, :2]  # Manter apenas as duas primeiras colunas
            df_prod.columns = ["Date", "Produced Energy (kWh)"]
            # Substituir vírgulas por pontos nas colunas numéricas, caso haja
            df_prod['Produced Energy (kWh)'] = df_prod['Produced Energy (kWh)'].str.replace(',', '.').astype(float)

        if uploaded_irradiance_data is not None:
            # Processar o arquivo de irradiância do sol relativamente à instalação
            df_irradiance = pd.read_csv(uploaded_irradiance_data, delimiter=",", skiprows=8)
            df_irradiance = df_irradiance.dropna()
            df_irradiance = df_irradiance[['G(i)']]  # Manter apenas a coluna 'G(i)'
            # Substituir vírgulas por pontos nas colunas numéricas, caso haja
            df_irradiance['G(i)'] = df_irradiance['G(i)'].str.replace(',', '.').astype(float)

            # Criar a tabela "kWh e G(i) do sistema real" juntando os dados de produção e irradiância
            df_real_system = df_prod.copy()  # Copiar a tabela de produção de energia
            df_real_system['G(i)'] = df_irradiance['G(i)']  # Adicionar a coluna G(i) à tabela

            # Filtrar os dados para criar a tabela "Dados Equivalentes Diários"
            df_filtered = df_real_system[(df_real_system['Produced Energy (kWh)'] >= 2) & 
                                          (df_real_system['G(i)'] >= 100)].copy()
            df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], format='%d/%m/%Y %H:%M', errors='coerce')
            df_filtered = df_filtered.dropna(subset=['Date'])  # Remover linhas com datas inválidas
            df_filtered['Date'] = df_filtered['Date'].dt.date  # Manter apenas a data
            
            # Calcular as médias diárias
            df_daily_avg = df_filtered.groupby('Date')[['Produced Energy (kWh)', 'G(i)']].mean().reset_index()

            # Calcular o declive (coeficiente angular da relação entre kWh e G(i))
            X = df_daily_avg[['G(i)']].values  # Variável independente
            y = df_daily_avg['Produced Energy (kWh)'].values  # Variável dependente

            # Criar o modelo de regressão linear sem intercepto
            model = LinearRegression(fit_intercept=False)
            model.fit(X, y)

            slope = model.coef_[0]  # Coeficiente angular (declive)
            r_squared = model.score(X, y)  # R² sem intercepto

            # Calcular a eficiência do sistema
            efficiency = (1000 / (num_panels * panel_area)) * slope * 100

            # Exibir o declive, R², e a eficiência do sistema
            st.subheader("Resultados da Eficiência do Sistema")
            st.write(f"**Eficiência do Sistema (%):** {efficiency:.2f}")

            # Cálculos para multiplicar os valores de G(i) pelo declive e calcular a taxa de erro
            df_real_system_nonzero = df_real_system[df_real_system['Produced Energy (kWh)'] > 0]
            df_real_system_nonzero['Theoretical kWh'] = df_real_system_nonzero['G(i)'] * slope

            total_theoretical_kwh = df_real_system_nonzero['Theoretical kWh'].sum()
            total_real_kwh = df_real_system_nonzero['Produced Energy (kWh)'].sum()
            error_rate = abs(total_theoretical_kwh - total_real_kwh) / total_real_kwh * 100

            st.subheader("Cálculo da Taxa de Erro")
            st.write(f"**Total de kWh Reais:** {total_real_kwh:.2f} kWh")
            st.write(f"**Total de kWh Estimados Pelo Programa:** {total_theoretical_kwh:.2f} kWh")
            st.write(f"**Taxa de Erro (%):** {error_rate:.2f}")

        if uploaded_irradiance_desired_data is not None:
            # Processar o arquivo de irradiância do sol para a instalação desejada
            df_irradiance_desired = pd.read_csv(uploaded_irradiance_desired_data, delimiter=",", skiprows=8)
            df_irradiance_desired = df_irradiance_desired.dropna()
            df_irradiance_desired = df_irradiance_desired[['G(i)']]  # Manter apenas a coluna 'G(i)'
            # Substituir vírgulas por pontos nas colunas numéricas, caso haja
            df_irradiance_desired['G(i)'] = df_irradiance_desired['G(i)'].str.replace(',', '.').astype(float)

            # Criar a tabela "kWh e G(i) do Sistema Teórico"
            df_theoretical_system = df_prod.copy()  # Copiar a tabela de produção de energia
            df_theoretical_system['G(i) Desired'] = df_irradiance_desired['G(i)']  # Adicionar a coluna G(i) para a instalação desejada

            # Calcular os kWh Teóricos multiplicando os valores de G(i) Desired pelo declive
            df_theoretical_system_nonzero = df_theoretical_system[df_theoretical_system['Produced Energy (kWh)'] > 0]
            df_theoretical_system_nonzero['Theoretical kWh'] = df_theoretical_system_nonzero['G(i) Desired'] * slope

            total_theoretical_kwh_new = df_theoretical_system_nonzero['Theoretical kWh'].sum()

            # Calcular o aumento percentual em relação ao valor anterior
            increase_percentage = ((total_theoretical_kwh_new - total_theoretical_kwh) / total_theoretical_kwh) * 100

            st.subheader("Resultados do Sistema Teórico")
            st.write(f"**Total de kWh Estimado:** {total_theoretical_kwh_new:.2f} kWh")
            st.write(f"**Aumento Percentual em relação ao Sistema Real:** {increase_percentage:.2f}%")

# Chamar a função para exibir a interface
show_interface()
