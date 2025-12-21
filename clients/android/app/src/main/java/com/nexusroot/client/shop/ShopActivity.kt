package com.nexusroot.client.shop

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.android.billingclient.api.ProductDetails
import com.nexusroot.client.R
import com.nexusroot.client.billing.BillingManager
import com.nexusroot.client.network.NetworkClient
import kotlinx.coroutines.launch

class ShopActivity : AppCompatActivity() {

    private lateinit var billingManager: BillingManager
    private lateinit var tvStatus: TextView

    // Product details map
    private val productDetailsMap = mutableMapOf<String, ProductDetails>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_shop)

        tvStatus = findViewById(R.id.tvStatus)

        billingManager = BillingManager(this,
            onPurchaseSuccess = { purchase ->
                // Verify with backend
                verifyPurchase(purchase.purchaseToken, purchase.products.firstOrNull() ?: "")
            },
            onPurchaseError = { error ->
                Toast.makeText(this, error, Toast.LENGTH_LONG).show()
                tvStatus.text = "Error: $error"
            }
        )

        billingManager.startConnection {
            tvStatus.text = "Connected. Loading products..."
            queryProducts()
        }

        setupButtons()
    }

    private fun setupButtons() {
        findViewById<Button>(R.id.btnBuy1000).setOnClickListener { launchPurchase("nexus_coin_1000") }
        findViewById<Button>(R.id.btnBuy5000).setOnClickListener { launchPurchase("nexus_coin_5000") }
        findViewById<Button>(R.id.btnBuyVIP).setOnClickListener { launchPurchase("nexus_vip_lifetime") }
    }

    private fun queryProducts() {
        val skuList = listOf("nexus_coin_1000", "nexus_coin_5000", "nexus_vip_lifetime")
        billingManager.queryProducts(skuList) { detailsList ->
            runOnUiThread {
                if (detailsList.isEmpty()) {
                    tvStatus.text = "No products found (Check Google Play Console)"
                } else {
                    tvStatus.text = "Products loaded."
                    detailsList.forEach { details ->
                        productDetailsMap[details.productId] = details
                        // Could update button text with price here
                    }
                }
            }
        }
    }

    private fun launchPurchase(sku: String) {
        val details = productDetailsMap[sku]
        if (details != null) {
            billingManager.launchPurchaseFlow(this, details)
        } else {
            Toast.makeText(this, "Product not available", Toast.LENGTH_SHORT).show()
        }
    }

    private fun verifyPurchase(token: String, sku: String) {
        tvStatus.text = "Verifying purchase..."
        lifecycleScope.launch {
            try {
                // TODO: Update NetworkClient to have verifyPurchase endpoint
                // For now, simulate success or use a generic command execution if backend supported it
                // We will add `verifyPurchase` to NexusApi in the next steps

                val response = NetworkClient.api.verifyPurchase(
                    mapOf("purchase_token" to token, "sku" to sku, "player_name" to "android_user")
                )

                if (response.isSuccessful && response.body()?.success == true) {
                    tvStatus.text = "Purchase Successful! Items added."
                    Toast.makeText(this@ShopActivity, "Purchase Verified!", Toast.LENGTH_LONG).show()
                } else {
                    tvStatus.text = "Verification Failed: ${response.body()?.error}"
                }
            } catch (e: Exception) {
                tvStatus.text = "Network Error: ${e.message}"
            }
        }
    }
}
