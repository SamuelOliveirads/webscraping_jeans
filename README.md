# WebScraping - Jeans

**PROJETO EM CONSTRUÇÃO**

# 1. Problema de negócio

 Um grupo de empreendedores buscam entrar no mercado de moda nos EUA, para tal definem produzir calças jeans ao público masculino e vender em E-commerce, entretanto a falta de experiência não os permitem definir características como preço, tipo de calças e materiais de fabricação, para tal solicitaram uma consultoria de Ciência de Dados com o objetivo de responder as seguintes perguntas:
  - Qual o melhor preço de venda para as calças?
  - Quantos tipos de calças e suas cores para o produto inicial?
  - Quais as matérias-primas necessárias para confeccionar as calças?

# 2. Suposições de negócio


# Lista de atributos
|Atributos | Descrição |
|----------|-----------|
| product_id       | identificador único do produto |  
| style_id         | identificador para o estilo    |  
| color_id         | identificador para a cor       |  
| product_name     | nome da calça jeans            |  
| color_name       | nome da cor da calça           |  
| fit              | estilo de ajuste da calça      | 
| cotton           | quantidade da materia-prima utilizada (%) |  
| polyester        | quantidade da materia-prima utilizada (%) |  
| elastomultiester | quantidade da materia-prima utilizada (%) |   
| spandex          | quantidade da materia-prima utilizada (%) |   
| material         | tipo de tecido da calça        | 
| description      | descrição da cor da calça      |  
| scrapy_datetime  | Data da coleta dos dados       |    

# 3. A solução

 Para a resolução é utilizado os dados da empresa H&M e Macys, o objetivo será coletar a maior quantidade de informações relevantes de cada calça disponíveis em ambos os sites e realizar uma análise que disponibilize relatórios com as informações de preço, cor e materiais, assim como também Insights.
 O resultado do projeto estará disponível via aplicação website para que a equipe de empreendedores possam acessar e filtrar as informações.

# Estratégia da solução

Para resolver o problema de negócio utilizo da metodologia CRISP-DM adaptada para os processos de ciência de dados, as etapas de processos para a solução serão as seguintes:

Minha metodologia utilizou dos seguintes princípios:

**Step 01. Data collection:** Realizo um estudo dos sites quanto a sua estrutura e dados disponíveis, crio um sistema de coleta em ETL e com agendamento de Jobs para preencher os dados em um Bancos de Dados SQLite.

**Step 01. Data Description:** Realizo uma análise breve dos dados e suas estatísticas, também limpo alguns dados com potenciais comprometedoras, o foco está em ganhar conhecimento inicial do problema em que estou lidando, em um ambiente de trabalho esta etapa engloba a extração dos dados do banco de dados ou da internet através da técnica de Web Scrapping.

# 4. Top 5 Insights de negócio
 - Em construção

# 5. Resultados de negócio
 - Em construção

# 6. Modelo em produção
 - Em construção

# 7. Lições aprendidas
 - **Coleta dos dados:** Para realizar um bom Webscraping é necessário um excelente planejamento quanto as informações importantes, percebi que em momentos coletava informações irrelevantes ou redundantes, precisei filtrar algumas informações e a consequência é a perca de algumas coletas realizadas anteriormente.
 - **Verificação dos dados:** O processo de Webscraping traz bastante relevância ao tratamento dos dados, a falta do mesmo inseria sujeira nas informações e criava distorções nas análises, compreendi que deve ser feito um excelente planejamento e continua observação do coletado para evitar problemas posteriores.

# 8. Próximos passos
- Uma informação crítica quanto ao tamanho de cada peça não pode ser coletado devido a particularidade do site, a falta dessa informações prejudica quanto a uma análise dos possíveis tamanhos mais vendidos.
