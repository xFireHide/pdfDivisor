"""
App desktop: PDF da Shopee (4 etiquetas por página) → uma etiqueta por página.
Interface gráfica (tkinter / ttk).
"""
from __future__ import annotations

import queue
import threading
from io import BytesIO
from pathlib import Path
import fitz
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from processor import PDFPasswordError, process_pdf


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Processador de etiquetas PDF")
        self.minsize(520, 380)
        self._input_path: Path | None = None
        self._result_queue: queue.Queue[tuple] = queue.Queue()
        self._busy = False

        self._build_ui()
        self._center_window()

    def _build_ui(self) -> None:
        pad = {"padx": 16, "pady": 8}
        outer = ttk.Frame(self, padding=20)
        outer.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(outer, text="processador de etiquetas", font=("", 14, "bold"))
        title.pack(anchor=tk.W, **pad)

        hint = ttk.Label(
            outer,
            text="Ola, Diana....",
            wraplength=460,
            justify=tk.LEFT,
        )
        hint.pack(anchor=tk.W, padx=16, pady=(0, 12))

        ttk.Separator(outer, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        path_frame = ttk.Frame(outer)
        path_frame.pack(fill=tk.X, **pad)
        ttk.Label(path_frame, text="Arquivo PDF:").pack(anchor=tk.W)
        self._path_var = tk.StringVar(value="Nenhum arquivo selecionado")
        self._path_entry = ttk.Entry(path_frame, textvariable=self._path_var, state="readonly")
        self._path_entry.pack(fill=tk.X, pady=(4, 8))

        btn_row = ttk.Frame(outer)
        btn_row.pack(fill=tk.X, **pad)
        self._btn_open = ttk.Button(btn_row, text="Selecionar PDF…", command=self._choose_pdf)
        self._btn_open.pack(side=tk.LEFT)
        self._btn_run = ttk.Button(
            btn_row,
            text="Processar e salvar como…",
            command=self._start_process,
            state=tk.DISABLED,
        )
        self._btn_run.pack(side=tk.LEFT, padx=(12, 0))

        ttk.Separator(outer, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        self._status_var = tk.StringVar(value="Pronto.")
        self._status = ttk.Label(outer, textvariable=self._status_var, foreground="#333")
        self._status.pack(anchor=tk.W, **pad)

        self._progress = ttk.Progressbar(outer, mode="indeterminate", length=400)
        self._progress.pack(fill=tk.X, **pad)

        foot = ttk.Label(
            outer,
            text="Uso pessoal — valide uma página de teste antes de imprimir em lote.",
            font=("", 9),
            foreground="#666",
        )
        foot.pack(side=tk.BOTTOM, anchor=tk.W, pady=(16, 0))

    def _center_window(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _choose_pdf(self) -> None:
        if self._busy:
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Selecione o PDF das etiquetas (ex.: Shopee)",
            filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return
        self._input_path = Path(path)
        self._path_var.set(str(self._input_path))
        self._btn_run.configure(state=tk.NORMAL)
        self._status_var.set("Arquivo selecionado. Clique em “Processar e salvar como…”.")

    def _request_password_if_needed(self, raw: bytes) -> str | None:
        """
        Abre o PDF na thread principal. Se estiver protegido, pede a senha ao usuário.
        Retorna: "" se não precisa de senha, a senha se ok, None se o usuário cancelou.
        """
        try:
            doc = fitz.open(stream=BytesIO(raw), filetype="pdf")
        except RuntimeError as e:
            msg = str(e)
            messagebox.showerror(
                "Erro ao abrir PDF",
                f"Não foi possível abrir o arquivo:\n{msg}",
                parent=self,
            )
            return None

        try:
            if not doc.needs_pass:
                return ""
            while True:
                pwd = simpledialog.askstring(
                    "PDF protegido por senha",
                    "Este documento está criptografado ou fechado sem senha "
                    '(mensagens como "document closed or encrypted").\n\n'
                    "Digite a senha para abrir:",
                    show="*",
                    parent=self,
                )
                if pwd is None:
                    return None
                if doc.authenticate(pwd):
                    return pwd
                messagebox.showerror(
                    "Senha incorreta",
                    "A senha não abriu o PDF. Tente novamente.",
                    parent=self,
                )
        finally:
            doc.close()

    def _start_process(self) -> None:
        if self._busy or not self._input_path:
            return

        try:
            raw = self._input_path.read_bytes()
        except OSError as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{e}", parent=self)
            return

        password = self._request_password_if_needed(raw)
        if password is None:
            self._status_var.set("Operação cancelada ou falha ao abrir o PDF.")
            return

        self._busy = True
        self._btn_open.configure(state=tk.DISABLED)
        self._btn_run.configure(state=tk.DISABLED)
        self._status_var.set("Processando… pode levar alguns segundos.")
        self._progress.start(12)

        def worker() -> None:
            try:
                out = process_pdf(BytesIO(raw), password=password)
                self._result_queue.put(("ok", out))
            except PDFPasswordError as e:
                self._result_queue.put(("err", str(e)))
            except Exception as e:
                self._result_queue.put(("err", str(e)))

        threading.Thread(target=worker, daemon=True).start()
        self.after(100, self._poll_result)

    def _poll_result(self) -> None:
        try:
            kind, payload = self._result_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_result)
            return

        self._progress.stop()
        self._busy = False
        self._btn_open.configure(state=tk.NORMAL)
        self._btn_run.configure(state=tk.NORMAL if self._input_path else tk.DISABLED)

        if kind == "err":
            messagebox.showerror("Erro ao processar", payload, parent=self)
            self._status_var.set("Erro ao processar.")
            return

        out_buffer: BytesIO = payload
        default_name = f"{self._input_path.stem}_1-etiqueta-por-pagina.pdf"
        out_path = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar PDF processado",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF", "*.pdf")],
        )
        if not out_path:
            self._status_var.set("Processamento concluído. Salvamento cancelado.")
            return
        try:
            Path(out_path).write_bytes(out_buffer.getvalue())
        except OSError as e:
            messagebox.showerror("Erro ao salvar", str(e), parent=self)
            self._status_var.set("Não foi possível salvar o arquivo.")
            return

        self._status_var.set(f"Salvo: {out_path}")
        messagebox.showinfo("Concluído", f"PDF salvo em:\n{out_path}", parent=self)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
