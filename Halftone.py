import streamlit as st
from PIL import Image, ImageOps
from rembg import remove
import io

st.set_page_config(page_title="Gerador Halftone DTF Pro", page_icon="🖨️", layout="centered")

st.title("🖨️ Gerador de Halftone Automático para DTF")
st.subheader("Transforme as suas estampas: economize tinta e ganhe toque zero!")

uploaded_file = st.file_uploader("Arraste ou selecione uma imagem (PNG transparente ou JPEG com fundo)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    input_image = Image.open(uploaded_file).convert("RGBA")
    st.image(input_image, caption="Imagem Original", use_container_width=True)
    
    st.sidebar.header("🎛️ Configurações do Halftone")
    remover_fundo = st.sidebar.checkbox("Remover fundo da imagem automaticamente", value=True)
    lpi = st.sidebar.slider("Tamanho dos Pontos (LPI / Resolução)", min_value=10, max_value=60, value=35, step=5)
    
    if st.button("✨ Gerar Halftone para DTF"):
        with st.spinner("A processar imagem e inteligência artificial..."):
            if remover_fundo:
                processed_img = remove(input_image)
            else:
                processed_img = input_image
                
            r, g, b, alpha = processed_img.split()
            gray_image = processed_img.convert("L")
            
            scale_factor = lpi / 10.0
            new_size = (int(gray_image.width * scale_factor), int(gray_image.height * scale_factor))
            
            halftone = gray_image.resize(new_size, Image.Resampling.BILINEAR)
            halftone = halftone.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
            halftone = halftone.resize(gray_image.size, Image.Resampling.NEAREST).convert("L")
            
            output_image = Image.merge("RGBA", (halftone, halftone, halftone, alpha))
            
            st.success("✅ Halftone gerado com sucesso!")
            st.image(output_image, caption="Visualização do Halftone (Pronto para DTF)", use_container_width=True)
            
            buf = io.BytesIO()
            output_image.save(buf, format="PNG", dpi=(300, 300))
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Baixar PNG Reticulado (300 DPI)",
                data=byte_im,
                file_name="estampa_halftone_dtf.png",
                mime="image/png"
            )
