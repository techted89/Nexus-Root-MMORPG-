package com.nexusroot.client

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.nexusroot.client.viewmodel.MainViewModel

class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    private lateinit var tvOutput: TextView
    private lateinit var etInput: EditText
    private lateinit var btnSend: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvOutput = findViewById(R.id.tvOutput)
        etInput = findViewById(R.id.etInput)
        btnSend = findViewById(R.id.btnSend)

        // Observe ViewModel
        viewModel.consoleOutput.observe(this) { text ->
            tvOutput.text = text
            scrollToBottom()
        }

        btnSend.setOnClickListener {
            val cmd = etInput.text.toString()
            viewModel.sendCommand(cmd)
            etInput.text.clear()
        }
    }

    private fun scrollToBottom() {
        val scrollAmount = tvOutput.layout?.getLineTop(tvOutput.lineCount) ?: 0
        if (scrollAmount > tvOutput.height) {
            tvOutput.scrollTo(0, scrollAmount - tvOutput.height)
        }
    }
}
