from flask import Flask, request, send_file
import fitz  # PyMuPDF
import io
import requests

app = Flask(__name__)

def baixar_pdf_do_drive(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.content
    else:
        raise Exception(f"Erro ao baixar PDF com ID {file_id}")

@app.route('/')
def index():
    return 'Use /gerar?timbre=ID1&conteudo=ID2 para gerar PDF com sobreposição.'

@app.route('/gerar')
def gerar_pdf():
    id_timbre = request.args.get("timbre")
    id_conteudo = request.args.get("conteudo")

    if not id_timbre or not id_conteudo:
        return "IDs do Drive não informados. Exemplo: /gerar?timbre=ID1&conteudo=ID2", 400

    try:
        pdf_timbre = baixar_pdf_do_drive(id_timbre)
        pdf_conteudo = baixar_pdf_do_drive(id_conteudo)

        doc_timbre = fitz.open(stream=pdf_timbre, filetype="pdf")
        doc_conteudo = fitz.open(stream=pdf_conteudo, filetype="pdf")

        output_pdf = fitz.open()

        for i in range(len(doc_conteudo)):
            page_conteudo = doc_conteudo.load_page(i)

            idx_timbre = i if i < len(doc_timbre) else 0
            page_timbre = doc_timbre.load_page(idx_timbre)

            new_page = output_pdf.new_page(width=page_conteudo.rect.width, height=page_conteudo.rect.height)

            new_page.show_pdf_page(page_conteudo.rect, doc_conteudo, i)
            new_page.show_pdf_page(page_timbre.rect, doc_timbre, idx_timbre)

        output_stream = io.BytesIO()
        output_pdf.save(output_stream)
        output_stream.seek(0)

        return send_file(output_stream, download_name="pdf_final.pdf", as_attachment=False)

    except Exception as e:
        return f"Erro ao processar: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
