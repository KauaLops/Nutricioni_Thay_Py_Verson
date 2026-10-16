import os
from datetime import date, timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from .extensions import db
from .models import Contato, Post, Servico, Trabalho, Usuario


def hash_senha(senha):
    return generate_password_hash(senha, method="pbkdf2:sha256:600000")


def inicializar():
    """Idempotente: cria tabelas, o administrador inicial e conteúdo de demonstração."""
    db.create_all()
    if Usuario.query.count() == 0:
        email, senha = os.getenv("ADMIN_EMAIL", "").strip().lower(), os.getenv("ADMIN_PASSWORD", "")
        if email and len(senha) >= 8:
            db.session.add(Usuario(nome=os.getenv("ADMIN_NOME", "Thayane Luíze"), email=email, senha=hash_senha(senha)))
    if Contato.query.count() == 0:
        db.session.add(Contato(id=1, email="alcantarathayaneluize@gmail.com", telefone="+55 83 9830-1634",
                               whatsapp="+55 83 9830-1634", instagram="thayaneluize.nutri", crn="49735"))
    if Servico.query.count() == 0:
        for n, d, p, b in [
            ("Consulta Nutricional", "Primeiro atendimento com anamnese completa e plano alimentar individualizado.", "180.00",
             "Anamnese detalhada\nPlano alimentar personalizado\nOrientações para a rotina"),
            ("Avaliação Nutricional", "Avaliação do estado nutricional e da composição corporal.", "150.00",
             "Medidas e antropometria\nAnálise de hábitos\nRelatório com metas"),
            ("Retorno", "Reavaliação da evolução e ajustes no plano alimentar.", "100.00",
             "Análise da evolução\nAjustes no plano\nTira-dúvidas"),
            ("Acompanhamento Mensal", "Suporte contínuo durante o mês para manter a constância.", "350.00",
             "Consultas de retorno\nSuporte entre as consultas\nAjustes sempre que preciso")]:
            db.session.add(Servico(nome=n, descricao=d, preco=Decimal(p), beneficios=b))
    if Trabalho.query.count() == 0:
        for t, d, c, i in [
            ("Congresso Conecta · CRN-6", "Participação em evento de atualização profissional em nutrição.", "Eventos", "/images/trabalho-1.jpg"),
            ("Atividade prática de campo", "Vivência prática em boas práticas e segurança dos alimentos.", "Formação", "/images/trabalho-2.jpg"),
            ("Estágio em ambiente clínico", "Experiência de atuação no cuidado nutricional em serviço de saúde.", "Clínica", "/images/trabalho-3.jpg")]:
            db.session.add(Trabalho(titulo=t, descricao=d, categoria=c, imagem_url=i))
    if Post.query.count() == 0:
        hoje = date.today()
        for i, (t, r, c, dias, txt) in enumerate([
            ("Alimentação saudável começa no planejamento", "Organizar a semana facilita escolhas melhores e reduz o improviso na hora da fome.", "Alimentação saudável", 3,
             "Comer bem não exige receitas complicadas. Reserve um momento da semana para pensar nas refeições e fazer uma lista de compras com alimentos in natura.\n\nTer frutas, verduras e proteínas já preparadas ajuda a manter a constância nos dias corridos.\n\nCada pessoa tem necessidades diferentes: um plano individualizado, feito com acompanhamento profissional, torna o processo mais leve."),
            ("A importância da hidratação", "A água participa de funções essenciais do corpo, e pequenos lembretes ajudam a beber mais ao longo do dia.", "Hidratação", 10,
             "A água participa da regulação da temperatura, da digestão e do transporte de nutrientes.\n\nPara criar o hábito, mantenha uma garrafa por perto e associe os goles a momentos da rotina, como ao acordar e antes das refeições.\n\nA quantidade ideal varia com idade, clima e atividade física. Converse com o seu nutricionista."),
            ("Como montar um prato equilibrado", "Um prato colorido, com variedade e porções adequadas, é um bom ponto de partida.", "Prato equilibrado", 17,
             "Uma referência prática: metade do prato com verduras e legumes, uma parte com fonte de proteína e outra com carboidratos de boa qualidade, como arroz, feijão e tubérculos.\n\nQuanto mais colorido, maior a variedade de nutrientes. Coma com calma e atenção aos sinais de fome e saciedade."),
            ("Alimentação e qualidade de vida", "O que comemos influencia energia, humor, sono e disposição no dia a dia.", "Qualidade de vida", 24,
             "Alimentação equilibrada é um dos pilares do bem-estar, junto com sono de qualidade, atividade física e cuidado emocional.\n\nMudanças pequenas e sustentáveis costumam funcionar melhor do que dietas rígidas e passageiras."),
            ("Hábitos alimentares: por onde começar?", "Mudar hábitos é um processo. Comece por um passo possível e avance aos poucos.", "Hábitos alimentares", 31,
             "Escolha um hábito para trabalhar por vez: incluir uma fruta ao dia, reduzir ultraprocessados ou fazer as refeições sem telas.\n\nCelebre o progresso e seja gentil com os dias difíceis. O acompanhamento nutricional ajuda a adaptar as metas à sua realidade.")], 1):
            db.session.add(Post(titulo=t, resumo=r, categoria=c, conteudo=txt, imagem_url=f"/images/blog-{i}.svg",
                                data_publicacao=hoje - timedelta(days=dias)))
    db.session.commit()
