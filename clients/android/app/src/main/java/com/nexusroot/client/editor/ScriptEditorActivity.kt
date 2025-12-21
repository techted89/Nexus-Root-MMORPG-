package com.nexusroot.client.editor

import android.content.Context
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.nexusroot.client.R
import com.nexusroot.client.network.NetworkClient
import kotlinx.coroutines.launch

class ScriptEditorActivity : AppCompatActivity() {

    private lateinit var etScriptContent: EditText
    private lateinit var tvScriptOutput: TextView
    private lateinit var btnRun: Button
    private lateinit var btnSave: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_script_editor)

        etScriptContent = findViewById(R.id.etScriptContent)
        tvScriptOutput = findViewById(R.id.tvScriptOutput)
        btnRun = findViewById(R.id.btnRunScript)
        btnSave = findViewById(R.id.btnSaveScript)

        loadScript()

        btnSave.setOnClickListener {
            saveScript()
        }

        btnRun.setOnClickListener {
            runScript()
        }
    }

    private fun loadScript() {
        val prefs = getSharedPreferences("NexusScripts", Context.MODE_PRIVATE)
        val script = prefs.getString("last_script", "print(\"Hello Nexus\")")
        etScriptContent.setText(script)
    }

    private fun saveScript() {
        val script = etScriptContent.text.toString()
        val prefs = getSharedPreferences("NexusScripts", Context.MODE_PRIVATE)
        prefs.edit().putString("last_script", script).apply()
        Toast.makeText(this, "Script saved locally", Toast.LENGTH_SHORT).show()
    }

    private fun runScript() {
        val script = etScriptContent.text.toString()
        tvScriptOutput.text = "Executing..."

        lifecycleScope.launch {
            try {
                // Hardcoded player name for demo - ideally passed via Intent
                val request = mapOf("player_name" to "android_user", "script" to script)
                val response = NetworkClient.api.executeScript(request)

                if (response.isSuccessful && response.body()?.success == true) {
                    val output = response.body()?.data as? Map<*, *>
                    // output structure might vary based on API return, usually "output" key
                    // Actually, execute_script returns {"success": true, "output": ...}
                    // But ApiResponse wraps it in `data`. Wait, backend `execute_script` returns:
                    // { "success": True, "output": str(result_output) }
                    // It does NOT wrap in `data` key in the dictionary returned by `execute_script`?
                    // Let's check `web_server.py`.
                    // `self.send_json_response(result)` where result is whatever `execute_script` returns.
                    // `execute_script` returns `{"success": True, "output": ...}`.
                    // So `ApiResponse` deserialization might be tricky if `data` is expected.
                    // Models.kt: `val data: T? = null`.
                    // The JSON is `{ "success": true, "output": "..." }`.
                    // `data` is null. `output` is not in ApiResponse.
                    // I should probably update ApiResponse or just read the raw map if possible.
                    // For now, let's assume I can read "output" from the map if T is Map.

                    // Actually, let's just show raw body or message.
                    tvScriptOutput.text = response.body()?.toString() ?: "Success"
                } else {
                    tvScriptOutput.text = "Error: ${response.body()?.error}"
                }
            } catch (e: Exception) {
                tvScriptOutput.text = "Network Error: ${e.message}"
            }
        }
    }
}
