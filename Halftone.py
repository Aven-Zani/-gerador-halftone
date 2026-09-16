import streamlit as st
from PIL import Image, ImageOps
import io

# Configuração da página do App
st.set_page_config(page_title="Gerador Halftone DTF Pro", page_icon="🖨️", layout="centered")

st.title("🖨️ Gerador de Halftone Automático para DTF")
st.subheader("Transforme as suas estampas: economize tinta e ganhe toque zero!")

# Upload da imagem pelo utilizador
uploaded_file = st.file_uploader("Arraste ou selecione uma imagem (PNG com fundo transparente)", type=["png"])

if uploaded_file is not None:
    # Abrir imagem original
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    st.image(input_image, caption="Imagem Original", use_container_width=True)
    
    st.sidebar.header("🎛️ Configurações do Halftone")
    
    # Sliders para o utilizador ajustar o efeito
    lpi = st.sidebar.slider("Tamanho dos Pontos (LPI / Resolução)", min_value=10, max_value=60, value=35, step=5)
    
    if st.button("✨ Gerar Halftone para DTF"):
        with st.spinner("A processar imagem..."):
            # Separar o canal Alpha (transparência) para preservar o fundo recortado do DTF
            r, g, b, alpha = input_image.split()
            
            # Converter a imagem colorida para escala de cinzentos (L) para aplicar o meio-tom
            gray_image = input_image.convert("L")
            
            # Algoritmo de Halftone nativo do PIL via modo Bitmap (1) com dithering
            # O tamanho (lpi) define o quão espessos serão os pontos na conversão
            scale_factor = lpi / 10.0
            new_size = (int(gray_image.width * scale_factor), int(gray_image.height * scale_factor))
            
            # Reduz e expande para criar o efeito quadriculado/reticulado de pontos
            halftone = gray_image.resize(new_size, Image.Resampling.BILINEAR)
            halftone = halftone.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
            halftone = halftone.resize(gray_image.size, Image.Resampling.NEAREST).convert("L")
            
            # Recriar a imagem final colorida aplicando a máscara do Halftone e mantendo o canal Alpha original
            final_r = ImageOps.fit(r, halftone.size)
            final_g = ImageOps.fit(g, halftone.size)
            final_b = ImageOps.fit(b, halftone.size)
            
            # Combinar os canais: a retícula corta a intensidade das cores e da base branca
            output_image = Image.merge("RGBA", (halftone, halftone, halftone, alpha))
            
            # Mostrar resultado na ecrã
            st.success("✅ Halftone gerado com sucesso!")
            st.image(output_image, caption="Visualização do Halftone (Pronto para DTF)", use_container_width=True)
            
            # Preparar o ficheiro para download em alta resolução (300 DPI)
            buf = io.BytesIO()
            output_image.save(buf, format="PNG", dpi=(300, 300))
            byte_im = buf.getvalue()
            
            # Botão de Download do PNG final
            st.download_button(
                label="📥 Baixar PNG Reticulado (300 DPI)",
                data=byte_im,
                file_name="estampa_halftone_dtf.png",
                mime="image/png"
            )
