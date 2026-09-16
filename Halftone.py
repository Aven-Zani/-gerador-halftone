import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
from rembg import remove
from openai import OpenAI
import io
import requests

# Configuração da página do App
st.set_page_config(page_title="Gerador Halftone DTF Pro", page_icon="🖨️", layout="centered")

# Palavra-passe Premium (Pode alterar quando quiser)
senha_premium_correta = "DTFPRO2026" 

# Inicializar o contador de imagens grátis (Limite de 5)
if "contador_gratis" not in st.session_state:
    st.session_state.contador_gratis = 0

st.title("🖨️ Gerador de Halftone Automático para DTF")
st.subheader("Transforme as suas estampas: economize tinta e ganhe toque zero!")

# --- ÁREA DE LOGIN DA ASSINATURA NA BARRA LATERAL ---
st.sidebar.markdown("### 🔑 Área do Assinante")
senha_usuario = st.sidebar.text_input("Introduza a sua Palavra-passe Premium:", type="password")
eh_premium = (senha_usuario == senha_premium_correta)

if eh_premium:
    st.sidebar.success("🔓 Modo Premium Ativo (Sem Limites + IA)")
else:
    imagens_restantes = max(0, 5 - st.session_state.contador_gratis)
    st.sidebar.info(f"🎁 Modo Gratuito: Restam-lhe {imagens_restantes} testes de Halftone básico.")

# --- VERIFICAÇÃO DE BLOQUEIO DE LIMITE ---
if not eh_premium and st.session_state.contador_gratis >= 5:
    st.error("⚠️ Atingiu o seu limite de 5 imagens gratuitas!")
    st.markdown("""
    ### 🚀 Faça a sua Assinatura para Desbloquear Acesso Ilimitado:
    Não pare a sua produção. Assine agora para ter acesso sem limites, modificar imagens com IA e libertar a remoção de fundos.
    
    * **💶 Plano Mensal (Uso Ilimitado):** 9,90 € / mês  
    * **💶 Plano Anual (Melhor Custo-Benefício):** 49,00 € / ano  
    """)
    st.link_button("💳 Assinar Plano Mensal (9,90€)", "https://stripe.com")
    st.link_button("🔥 Assinar Plano Anual (49,00€)", "https://stripe.com")
    st.stop()

# --- CARREGAMENTO DA IMAGEM ---
uploaded_file = st.file_uploader("Arraste ou selecione uma imagem (PNG transparente ou JPEG com fundo)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.header("🎛️ Configurações da Estampa")
    
    # Opção de remover fundo com IA (Apenas Premium)
    remover_fundo = st.sidebar.checkbox("Remover fundo da imagem automaticamente ✨ (Premium)")
    
    if remover_fundo and not eh_premium:
        st.sidebar.error("🔒 Função Exclusiva para Assinantes.")
        st.stop()

    # --- 🛠️ PAINEL DE EDIÇÃO E MODIFICAÇÃO COM IA ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Modificar Desenho com IA (Premium)")
    
    # Caixa de texto para descrever alterações no desenho
    comando_ia = st.sidebar.text_area("Descreva como quer modificar o desenho (ex: 'Mude as cores para dourado e adicione fogo ao fundo'):")
    
    if comando_ia and not eh_premium:
        st.error("🔒 Modificar desenhos através de comandos de Inteligência Artificial é uma função Premium.")
        st.markdown("### 💶 Ative o seu Plano para libertar o editor de IA:")
        st.link_button("💳 Assinar Plano Mensal (9,90€)", "https://stripe.com")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Ajustes Manuais")
    brilho = st.sidebar.slider("Brilho", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    contraste = st.sidebar.slider("Contraste", min_value=0.5, max_value=2.5, value=1.2, step=0.1)
    nitidez = st.sidebar.slider("Nitidez", min_value=0.5, max_value=3.0, value=1.5, step=0.1)
    
    # Aplicar os ajustes manuais
    edited_image = ImageEnhance.Brightness(input_image).enhance(brilho)
    edited_image = ImageEnhance.Contrast(edited_image).enhance(contraste)
    edited_image = ImageEnhance.Sharpness(edited_image).enhance(nitidez)
    
    st.image(edited_image, caption="Visualização da Imagem Atual", use_container_width=True)

    st.sidebar.markdown("---")
    lpi = st.sidebar.slider("Tamanho dos Pontos (LPI / Resolução Halftone)", min_value=10, max_value=60, value=35, step=5)
    
    if st.button("✨ Gerar Halftone para DTF"):
        with st.spinner("A processar imagem e Inteligência Artificial..."):
            
            img_para_processar = edited_image
            
            # --- MODELO PREMIUM: MODIFICAÇÃO DE IMAGEM VIA OPENAI DALL-E ---
            if comando_ia and eh_premium:
                try:
                    # Configurar a ligação segura à API da OpenAI (Lida através dos Segredos do Streamlit)
                    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                    
                    # Converter imagem atual para bytes para enviar para a OpenAI
                    img_byte_arr = io.BytesIO()
                    img_para_processar.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    # Chamar a IA para criar uma variação modificada com base no texto do utilizador
                    response = client.images.edit(
                        image=img_bytes,
                        prompt=comando_ia,
                        n=1,
                        size="1024x1024"
                    )
                    
                    # Descarregar a nova imagem gerada pela IA
                    image_url = response.data[0].url
                    response_img = requests.get(image_url)
                    img_para_processar = Image.open(io.BytesIO(response_img.content)).convert("RGBA")
                    st.info("🎨 O desenho foi modificado com sucesso pela IA!")
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA: Certifique-se de configurar a sua chave API nas definições do Streamlit.")
            
            # Executa a remoção de fundo com IA se selecionado
            if remover_fundo and eh_premium:
                img_para_processar = remove(img_para_processar)
                
            # Aplicar o algoritmo de meio-tom (Halftone)
            r, g, b, alpha = img_para_processar.split()
            gray_image = img_para_processar.convert("L")
            
            scale_factor = lpi / 10.0
            new_size = (int(gray_image.width * scale_factor), int(gray_image.height * scale_factor))
            
            halftone = gray_image.resize(new_size, Image.Resampling.BILINEAR)
            halftone = halftone.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
            halftone = halftone.resize(gray_image.size, Image.Resampling.NEAREST).convert("L")
            
            output_image = Image.merge("RGBA", (halftone, halftone, halftone, alpha))
            
            if not eh_premium:
                st.session_state.contador_gratis += 1
            
            st.success("✅ Halftone gerado com sucesso!")
            st.image(output_image, caption="Resultado Final Pronto para DTF", use_container_width=True)
            
            buf = io.BytesIO()
            output_image.save(buf, format="PNG", dpi=(300, 300))
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Baixar PNG Reticulado (300 DPI)",
                data=byte_im,
                file_name="estampa_halftone_dtf.png",
                mime="image/png"
            )
