package com.example.hoavision

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.runtime.MutableState
import com.example.hoavision.databinding.DetectMainBinding
import com.example.hoavision.fragments.CameraFragment
import java.text.SimpleDateFormat
import java.util.Date

class DetectActivity : AppCompatActivity(), CameraFragment.OnDataPassListener {

    private lateinit var detectMainBinding: DetectMainBinding
    var detectedImage = ""


    override fun onDataPassed(data: String) {
        Log.d("MainActivity", data)
        detectedImage = data
        runOnUiThread {
            val radioGroup = findViewById<RadioGroup>(R.id.radioGroup)
            val prompt = findViewById<TextView>(R.id.textView5)
            if(data.equals("trash") || data.equals("satellite") || data.equals("rv") || data.equals("dead grass")){
                radioGroup.visibility = View.VISIBLE
                prompt.text = data + " detected, would you like to report it to a house?";
            }
        }

    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        detectMainBinding = DetectMainBinding.inflate(layoutInflater)
        setContentView(detectMainBinding.root)

        val radioGroup = findViewById<RadioGroup>(R.id.radioGroup)
        radioGroup.visibility = View.INVISIBLE
        radioGroup.setOnCheckedChangeListener(
            RadioGroup.OnCheckedChangeListener { group, checkedId ->
                val radio: RadioButton = findViewById(checkedId)
                val sdf = SimpleDateFormat("dd/M/yyyy hh:mm:ss")
                val currentDate = sdf.format(Date())

                val prefs = getSharedPreferences("MyGlobalPrefs", MODE_PRIVATE)

                val violationList = prefs.getStringSet(radio.text.toString(), mutableSetOf())
                violationList?.add(detectedImage  + " detected at: " + currentDate)
                val editor = prefs.edit()
                editor.clear()
                println("bwaha" + violationList)
                editor.putStringSet(radio.text.toString(), violationList)
                println("bwaha" + violationList)
                editor.apply()
                editor.commit()



                Toast.makeText(this, radio.text.toString() + " reported for " + detectedImage, Toast.LENGTH_SHORT).show();
            })
        val radioGroupModelType = findViewById<RadioGroup>(R.id.radioGroupModelType)
        val house1 = findViewById<RadioButton>(R.id.house1)
        val house2 = findViewById<RadioButton>(R.id.house2)
        val house3 = findViewById<RadioButton>(R.id.house3)

    }


    override fun onBackPressed() {
        if (true) {
            val intent = Intent(
                this,
                LoginActivity::class.java
            )
            startActivity(intent)
            finishAfterTransition()
        } else {
            super.onBackPressed()
        }

    }

    private fun onClick(selectedOption: MutableState<String>, name: String) {

        val sdf = SimpleDateFormat("dd/M/yyyy hh:mm:ss")
        val currentDate = sdf.format(Date())

        val prefs = getSharedPreferences("MyGlobalPrefs", MODE_PRIVATE)

        val violationList = prefs.getStringSet(selectedOption.value, mutableSetOf())
        violationList?.add(name  + " detected at: " + currentDate)
        val editor = prefs.edit()

        editor.putStringSet(selectedOption.value, violationList)
        editor.apply()

        Toast.makeText(this, selectedOption.value + " reported for " + name, Toast.LENGTH_SHORT).show();
    }
}