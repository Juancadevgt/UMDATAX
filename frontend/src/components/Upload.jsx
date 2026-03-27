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

  // Toggle individual
  const toggleCampo = (campo) => {
    setCampos(prev =>
      prev.includes(campo)
        ? prev.filter(c => c !== campo)
        : [...prev, campo]
    );
  };

  // Seleccionar todos
  const seleccionarTodos = () => setCampos(CAMPOS);

  // Quitar todos
  const quitarTodos = () => setCampos([]);

  // 🔥 PROCESAR + DESCARGAR
  const handleSubmit = async () => {
    if (!file) return alert("Selecciona archivo");

    try {
      const blob = await procesarArchivo(file, tipo, campos);

      // Crear descarga automática
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
    <div style={{ padding: 20 }}>
      <h2>UMDATAX 🚀</h2>

      {/* Tipo */}
      <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
        <option value="ZIP">ZIP</option>
        <option value="XML">XML</option>
      </select>

      <br /><br />

      {/* Archivo */}
      <input
        type="file"
        accept=".zip,.xml"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      {/* Dropdown botón */}
      <button onClick={() => setVisible(!visible)}>
        {visible ? "Ocultar campos ▲" : "Seleccionar campos ▼"}
      </button>

      {/* Dropdown */}
      {visible && (
        <div style={{
          border: "1px solid #444",
          padding: 10,
          marginTop: 10,
          maxHeight: 200,
          overflow: "auto",
          borderRadius: 8
        }}>
          {/* Botones */}
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

          {/* Checkboxes */}
          {CAMPOS.map((campo) => (
            <label key={campo} style={{ display: "block" }}>
              <input
                type="checkbox"
                checked={campos.includes(campo)}
                onChange={() => toggleCampo(campo)}
                style={{
                  accentColor: "white", // ✔ blanco
                  cursor: "pointer",
                  marginRight: 5
                }}
              />
              {campo}
            </label>
          ))}
        </div>
      )}

      <br />

      {/* Botón procesar */}
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
  );
}