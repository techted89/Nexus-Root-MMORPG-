package com.nexusroot.client

import android.os.Build
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.text.method.ScrollingMovementMethod
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Button
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import android.content.Intent
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.nexusroot.client.viewmodel.MainViewModel
import com.nexusroot.client.editor.ScriptEditorActivity
import java.util.*

class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    private lateinit var tvOutput: TextView
    private lateinit var etInput: AutoCompleteTextView
    private lateinit var btnSend: Button

    // HUD Elements
    private lateinit var tvPlayerName: TextView
    private lateinit var tvPlayerLevel: TextView
    private lateinit var tvPlayerCredits: TextView
    private lateinit var tvWalletAddress: TextView

    // Heat UI
    private lateinit var pbHeat: ProgressBar
    private lateinit var tvHeatValue: TextView

    // Animation Overlays
    private lateinit var overlayRadar: ImageView
    private lateinit var overlayHacking: TextView

    // Command History
    private val commandHistory = mutableListOf<String>()
    private var historyIndex = -1

    private lateinit var vibrator: Vibrator

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        vibrator = getSystemService(VIBRATOR_SERVICE) as Vibrator

        initializeViews()
        setupObservers()
        setupListeners()
        setupAutoComplete()
    }

    private fun initializeViews() {
        tvOutput = findViewById(R.id.tvOutput)
        etInput = findViewById(R.id.etInput)
        btnSend = findViewById(R.id.btnSend)

        tvPlayerName = findViewById(R.id.tvPlayerName)
        tvPlayerLevel = findViewById(R.id.tvPlayerLevel)
        tvPlayerCredits = findViewById(R.id.tvPlayerCredits)
        tvWalletAddress = findViewById(R.id.tvWalletAddress)

        pbHeat = findViewById(R.id.pbHeat)
        tvHeatValue = findViewById(R.id.tvHeatValue)

        overlayRadar = findViewById(R.id.overlayRadar)
        overlayHacking = findViewById(R.id.overlayHacking)

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

                // Update Heat
                val heat = player.virtual_computer?.heat ?: 0f
                val maxHeat = player.virtual_computer?.max_heat ?: 100f
                pbHeat.max = maxHeat.toInt()
                pbHeat.progress = heat.toInt()
                tvHeatValue.text = "${heat.toInt()}%"

                // Change color if overheated
                if (heat > maxHeat * 0.9) {
                    pbHeat.progressTintList = ContextCompat.getColorStateList(this, android.R.color.holo_red_dark)
                } else {
                    pbHeat.progressTintList = ContextCompat.getColorStateList(this, android.R.color.holo_red_light)
                }
            }
        }
    }

    private fun setupListeners() {
        btnSend.setOnClickListener {
            val cmd = etInput.text.toString()
            if (cmd.isNotBlank()) {
                commandHistory.add(cmd)
                historyIndex = commandHistory.size

                triggerHapticFeedback()

                viewModel.sendCommand(cmd) { result ->
                   handleAnimationType(result.animation_type)
                }

                etInput.text.clear()
            }
        }

        // Quick Commands
        findViewById<Button>(R.id.btnCmdStatus).setOnClickListener { sendQuickCmd("status") }
        findViewById<Button>(R.id.btnCmdScan).setOnClickListener { sendQuickCmd("scan") }
        findViewById<Button>(R.id.btnCmdLs).setOnClickListener { sendQuickCmd("ls") }
        findViewById<Button>(R.id.btnCmdHelp).setOnClickListener { sendQuickCmd("help") }

        // Special Characters
        findViewById<Button>(R.id.btnCmdSlash).setOnClickListener { insertText("/") }
        findViewById<Button>(R.id.btnCmdDot).setOnClickListener { insertText(".") }

        // History Navigation
        findViewById<Button>(R.id.btnHistoryUp).setOnClickListener { navigateHistory(-1) }
        findViewById<Button>(R.id.btnHistoryDown).setOnClickListener { navigateHistory(1) }

        // Script Editor
        findViewById<Button>(R.id.btnOpenEditor).setOnClickListener {
            val intent = Intent(this, ScriptEditorActivity::class.java)
            startActivity(intent)
        }
    }

    private fun sendQuickCmd(cmd: String) {
        viewModel.sendCommand(cmd) { result ->
            handleAnimationType(result.animation_type)
        }
        triggerHapticFeedback()
    }

    private fun insertText(text: String) {
        etInput.text.append(text)
        etInput.setSelection(etInput.text.length)
        triggerHapticFeedback()
    }

    private fun navigateHistory(direction: Int) {
        if (commandHistory.isEmpty()) return

        historyIndex += direction
        historyIndex = historyIndex.coerceIn(0, commandHistory.size)

        if (historyIndex == commandHistory.size) {
            etInput.text.clear()
        } else {
            etInput.setText(commandHistory[historyIndex])
            etInput.setSelection(etInput.text.length)
        }
    }

    private fun setupAutoComplete() {
        val commands = arrayOf("help", "scan", "ls", "cat", "status", "hashcrack", "dos_attack", "set", "login", "register", "exit")
        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, commands)
        etInput.setAdapter(adapter)
    }

    private fun triggerHapticFeedback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createOneShot(20, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            vibrator.vibrate(20)
        }
    }

    private fun handleAnimationType(type: String?) {
        when (type) {
            "SCANNING_RADAR" -> playRadarAnimation()
            "HACKING_MATRIX" -> playHackingAnimation()
            "ERROR_SHAKE" -> playShakeAnimation()
            "SUCCESS_UNLOCK" -> playSuccessAnimation()
        }
    }

    private fun playRadarAnimation() {
        overlayRadar.visibility = View.VISIBLE
        val anim = AnimationUtils.loadAnimation(this, R.anim.radar_spin)
        overlayRadar.startAnimation(anim)

        overlayRadar.postDelayed({
            overlayRadar.clearAnimation()
            overlayRadar.visibility = View.GONE
        }, 2000)
    }

    private fun playHackingAnimation() {
        overlayHacking.visibility = View.VISIBLE
        val random = Random()
        val timer = Timer()
        var count = 0
        timer.schedule(object : TimerTask() {
            override fun run() {
                runOnUiThread {
                    val sb = StringBuilder()
                    for (i in 0..50) {
                        sb.append(if (random.nextBoolean()) "1" else "0")
                        if (i % 10 == 0) sb.append("\n")
                    }
                    overlayHacking.text = sb.toString()
                }
                count++
                if (count > 20) {
                    timer.cancel()
                    runOnUiThread { overlayHacking.visibility = View.GONE }
                }
            }
        }, 0, 100)
    }

    private fun playShakeAnimation() {
        val anim = AnimationUtils.loadAnimation(this, R.anim.shake)
        etInput.startAnimation(anim)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createOneShot(100, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            vibrator.vibrate(100)
        }
    }

    private fun playSuccessAnimation() {
         if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 50, 50, 50), -1))
        } else {
            vibrator.vibrate(200)
        }
    }
}
