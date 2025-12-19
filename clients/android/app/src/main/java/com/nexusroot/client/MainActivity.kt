package com.nexusroot.client

import android.os.Bundle
import android.text.method.ScrollingMovementMethod
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

    // HUD Elements
    private lateinit var tvPlayerName: TextView
    private lateinit var tvPlayerLevel: TextView
    private lateinit var tvPlayerCredits: TextView
    private lateinit var tvWalletAddress: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initializeViews()
        setupObservers()
        setupListeners()
    }

    private fun initializeViews() {
        tvOutput = findViewById(R.id.tvOutput)
        etInput = findViewById(R.id.etInput)
        btnSend = findViewById(R.id.btnSend)

        tvPlayerName = findViewById(R.id.tvPlayerName)
        tvPlayerLevel = findViewById(R.id.tvPlayerLevel)
        tvPlayerCredits = findViewById(R.id.tvPlayerCredits)
        tvWalletAddress = findViewById(R.id.tvWalletAddress)

        tvOutput.movementMethod = ScrollingMovementMethod()
    }

    private fun setupObservers() {
        viewModel.consoleOutput.observe(this) { text ->
            tvOutput.text = text
            scrollToBottom()
        }

        viewModel.playerStats.observe(this) { player ->
            if (player != null) {
                tvPlayerName.text = player.name
                tvPlayerLevel.text = "Lvl: ${player.level}"
                tvPlayerCredits.text = "NXC: ${player.credits}"
                tvWalletAddress.text = "Wallet: ${player.wallet_address ?: "Unknown"}"
            }
        }
    }

    private fun setupListeners() {
        btnSend.setOnClickListener {
            val cmd = etInput.text.toString()
            viewModel.sendCommand(cmd)
            etInput.text.clear()
        }

        // Quick Commands
        findViewById<Button>(R.id.btnCmdStatus).setOnClickListener {
            viewModel.sendCommand("status")
        }
        findViewById<Button>(R.id.btnCmdScan).setOnClickListener {
            viewModel.sendCommand("scan")
        }
        findViewById<Button>(R.id.btnCmdLs).setOnClickListener {
            viewModel.sendCommand("ls")
        }
        findViewById<Button>(R.id.btnCmdHelp).setOnClickListener {
            viewModel.sendCommand("help")
        }

        // Special Characters (insert into input)
        findViewById<Button>(R.id.btnCmdSlash).setOnClickListener {
            etInput.text.append("/")
            etInput.setSelection(etInput.text.length)
        }
        findViewById<Button>(R.id.btnCmdDot).setOnClickListener {
            etInput.text.append(".")
            etInput.setSelection(etInput.text.length)
        }
    }

    private fun scrollToBottom() {
        val scrollAmount = tvOutput.layout?.getLineTop(tvOutput.lineCount) ?: 0
        if (scrollAmount > tvOutput.height) {
            tvOutput.scrollTo(0, scrollAmount - tvOutput.height)
        }
    }
}
