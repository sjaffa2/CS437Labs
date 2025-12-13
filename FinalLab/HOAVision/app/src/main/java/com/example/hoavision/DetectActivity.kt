package com.example.hoavision

import com.example.hoavision.databinding.DetectMainBinding
import android.os.Bundle
import android.os.Build
import androidx.appcompat.app.AppCompatActivity
import android.util.Log

class DetectActivity : AppCompatActivity() {

    private lateinit var detectMainBinding: DetectMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        detectMainBinding = DetectMainBinding.inflate(layoutInflater)
        setContentView(detectMainBinding.root)
    }


    override fun onBackPressed() {
        if (Build.VERSION.SDK_INT == Build.VERSION_CODES.Q) {
            finishAfterTransition()
        } else {
            super.onBackPressed()
        }
    }
}