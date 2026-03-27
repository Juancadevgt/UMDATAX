import { useState } from "react";
import { procesarArchivo } from "../services/api";

const CAMPOS = [
  "AfiliacionIVA", "CodigoEstablecimiento", "CorreoEmisor",
  "NITEmisor", "NombreComercial", "NombreEmisor",
  "Direccion", "CodigoPostal", "Municipio",
  "Departamento", "Pais", "Frases"
];

export default function Upload() {
  const [file, setFile] = useState(null);
  const [tipo, setTipo] = useState("ZIP");
  const [campos, setCampos] = useState(CAMPOS);
  const [visible, setVisible] = useState(false);

  const toggleCampo = (campo) => {
    setCampos(prev =>
      prev.includes(campo)
        ? prev.filter(c => c !== campo)
        : [...prev, campo]
    );
  };

  const seleccionarTodos = () => setCampos(CAMPOS);
  const quitarTodos = () => setCampos([]);

  const handleSubmit = async () => {
    if (!file) return alert("Selecciona archivo");

    try {
      const blob = await procesarArchivo(file, tipo, campos);

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");

      a.href = url;
      a.download = "procesado.xlsx";

      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(url);

      alert("✅ Archivo descargado correctamente");

    } catch (error) {
      console.error(error);
      alert("❌ Error al procesar archivo");
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      padding: 20
    }}>

      {/* CONTENIDO PRINCIPAL */}
      <div>
        <h2 style={{ textAlign: "center" }}>UMDATAX 🚀</h2>

        <div style={{ textAlign: "center" }}>
          <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
            <option value="ZIP">ZIP</option>
            <option value="XML">XML</option>
          </select>

          <br /><br />

          <input
            type="file"
            accept=".zip,.xml"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <br /><br />

          <button onClick={() => setVisible(!visible)}>
            {visible ? "Ocultar campos ▲" : "Seleccionar campos ▼"}
          </button>

          {visible && (
            <div style={{
              border: "1px solid #444",
              padding: 10,
              marginTop: 10,
              maxHeight: 200,
              overflow: "auto",
              borderRadius: 8,
              display: "inline-block",
              textAlign: "left"
            }}>
              <div style={{ marginBottom: 10 }}>
                <button onClick={seleccionarTodos}>
                  Seleccionar todos
                </button>

                <button
                  onClick={quitarTodos}
                  style={{ marginLeft: 10 }}
                >
                  Quitar selección
                </button>
              </div>

              {CAMPOS.map((campo) => (
                <label key={campo} style={{ display: "block" }}>
                  <input
                    type="checkbox"
                    checked={campos.includes(campo)}
                    onChange={() => toggleCampo(campo)}
                    style={{
                      accentColor: "white",
                      cursor: "pointer",
                      marginRight: 5
                    }}
                  />
                  {campo}
                </label>
              ))}
            </div>
          )}

          <br /><br />

          <button
            onClick={handleSubmit}
            style={{
              background: "green",
              color: "white",
              padding: "6px 12px",
              border: "none",
              cursor: "pointer"
            }}
          >
            Procesar
          </button>
        </div>
      </div>

      {/* FOOTER PROFESIONAL */}
      <footer style={{
        marginTop: 40,
        paddingTop: 15,
        borderTop: "1px solid #333",
        textAlign: "center",
        fontSize: "12px",
        color: "#aaa"
      }}>
        <div style={{ marginBottom: 5 }}>
          Versión 1.0.0
        </div>

        <div style={{ marginBottom: 5 }}>
          Soporte: <span style={{ color: "#fff" }}>
            juan.jimenez@umbralcorp.com
          </span>
        </div>

        <div>
          Para agregar nuevos campos o tipos de archivos,
          contactar al correo de soporte.
        </div>
      </footer>

    </div>
  );
}