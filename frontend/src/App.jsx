import { useState } from "react";
import Upload from "./components/Upload";
import Reportes from "./components/Reportes";

export default function App() {
  const [modulo, setModulo] = useState(null);

  if (modulo === "xml") {
    return <Upload onVolver={() => setModulo(null)} />;
  }

  if (modulo === "pbi") {
    return <Reportes onVolver={() => setModulo(null)} />;
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: 20
    }}>

      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          marginBottom: 8
        }}>
          <img
            src="/logo2.png"
            alt="logo"
            style={{ width: 38, height: 38, objectFit: "contain" }}
          />
          <h2 style={{ margin: 0, fontSize: 24 }}>UMDATAX</h2>
        </div>
        <p style={{ margin: 0, color: "#aaa", fontSize: 14 }}>
          ¿Qué deseas hacer hoy?
        </p>
      </div>

      <div style={{
        display: "flex",
        gap: 20,
        flexWrap: "wrap",
        justifyContent: "center",
        maxWidth: 560
      }}>

        <div
          onClick={() => setModulo("xml")}
          style={{
            width: 220,
            border: "1px solid #444",
            borderRadius: 12,
            padding: "24px 20px",
            cursor: "pointer",
            textAlign: "center",
            transition: "border-color 0.2s"
          }}
          onMouseEnter={e => e.currentTarget.style.borderColor = "#888"}
          onMouseLeave={e => e.currentTarget.style.borderColor = "#444"}
        >
          <div style={{ fontSize: 32, marginBottom: 12 }}>📄</div>
          <p style={{ fontWeight: 600, fontSize: 15, margin: "0 0 8px" }}>
            Extractor XML / ZIP
          </p>
          <p style={{ fontSize: 13, color: "#aaa", margin: "0 0 16px", lineHeight: 1.5 }}>
            Procesa archivos XML y ZIP, extrae campos y exporta a Excel.
          </p>
          <span style={{
            fontSize: 12,
            background: "#1a3a1a",
            color: "#5cb85c",
            padding: "3px 10px",
            borderRadius: 20
          }}>
            Disponible
          </span>
        </div>

        <div
          onClick={() => setModulo("pbi")}
          style={{
            width: 220,
            border: "1px solid #1a6bb5",
            borderRadius: 12,
            padding: "24px 20px",
            cursor: "pointer",
            textAlign: "center",
            position: "relative",
            transition: "border-color 0.2s"
          }}
          onMouseEnter={e => e.currentTarget.style.borderColor = "#378ADD"}
          onMouseLeave={e => e.currentTarget.style.borderColor = "#1a6bb5"}
        >
          <span style={{
            position: "absolute",
            top: -11,
            left: "50%",
            transform: "translateX(-50%)",
            background: "#378ADD",
            color: "white",
            fontSize: 11,
            fontWeight: 600,
            padding: "2px 12px",
            borderRadius: 20,
            whiteSpace: "nowrap"
          }}>
            Nuevo
          </span>
          <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
          <p style={{ fontWeight: 600, fontSize: 15, margin: "0 0 8px" }}>
            Reportes Power BI
          </p>
          <p style={{ fontSize: 13, color: "#aaa", margin: "0 0 16px", lineHeight: 1.5 }}>
            Exporta reportes de Power BI a Excel sin licencia.
          </p>
          <span style={{
            fontSize: 12,
            background: "#0d2a3d",
            color: "#378ADD",
            padding: "3px 10px",
            borderRadius: 20
          }}>
            Disponible
          </span>
        </div>

      </div>

      <footer style={{
        marginTop: 60,
        textAlign: "center",
        fontSize: 12,
        color: "#555"
      }}>
        Versión 1.0.0 · Soporte: juan.jimenez@umbralcorp.com
      </footer>

    </div>
  );
}