package com.example.hoavision

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.camera.view.CameraController
import androidx.camera.view.LifecycleCameraController
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import com.example.hoavision.data.TfLiteLandmarkClassifier
import com.example.hoavision.domain.Classification
import com.example.hoavision.presentation.CameraPreview
import com.example.hoavision.presentation.LandmarkImageAnalyzer
import com.example.hoavision.ui.theme.HOAVisionTheme


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        if(!hasCameraPermission()) {
            ActivityCompat.requestPermissions(
                this, arrayOf(Manifest.permission.CAMERA), 0
            )
        }
        setContent {
            HOAVisionTheme {
                var classifications by remember {
                    mutableStateOf(emptyList<Classification>())
                }
                val analyzer = remember {
                    LandmarkImageAnalyzer(
                        classifier = TfLiteLandmarkClassifier(
                            context = applicationContext
                        ),
                        onResults = {
                            classifications = it
                        }
                    )
                }
                val controller = remember {
                    LifecycleCameraController(applicationContext).apply {
                        setEnabledUseCases(CameraController.IMAGE_ANALYSIS)
                        setImageAnalysisAnalyzer(
                            ContextCompat.getMainExecutor(applicationContext),
                            analyzer
                        )
                    }
                }
                Box(
                    modifier = Modifier
                        .size(425.dp, 900.dp)
                        .windowInsetsPadding(WindowInsets.statusBars)
                ) {
                    CameraPreview(controller, Modifier.size(425.dp, 500.dp))

                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .align(Alignment.TopCenter)
                    ) {
                        classifications.forEach {
                            Text(
                                text = it.name + " " + it.score*100 + "%",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(MaterialTheme.colorScheme.primaryContainer)
                                    .padding(8.dp),
                                textAlign = TextAlign.Center,
                                fontSize = 20.sp,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .align(Alignment.BottomCenter)
                    ) {
                        classifications.forEach {
                            //if(it.name == "Eiffel Tower" || it.name == "Big Ben"){
                                Text(
                                    text = it.name + " found, would you like to report it?",
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .background(MaterialTheme.colorScheme.primaryContainer)
                                        .padding(8.dp),
                                    textAlign = TextAlign.Center,
                                    fontSize = 20.sp,
                                    color = MaterialTheme.colorScheme.primary
                                )
                                val selectedOption = remember { mutableStateOf("Option1") }

                                Row (modifier = Modifier.size(400.dp, 100.dp)){
                                    RadioButton(
                                        selected = selectedOption.value == "House1",
                                        onClick = { selectedOption.value = "House1" }
                                    )
                                    Text("House1")

                                    RadioButton(
                                        selected = selectedOption.value == "House2",
                                        onClick = { selectedOption.value = "House2" }
                                    )
                                    Text("House2")

                                    RadioButton(
                                        selected = selectedOption.value == "House3",
                                        onClick = { selectedOption.value = "House3" }
                                    )
                                    Text("House3")
                                }
                                Row (modifier = Modifier.size(400.dp, 100.dp)){
                                    Button(onClick = { onClick(selectedOption, it.name) }) {
                                        Text("Submit")
                                    }
                                }


                            //}

                        }
                }

                }
            }
        }
    }

    private fun onClick(selectedOption: MutableState<String>, name: String) {

        val prefs = getSharedPreferences("MyGlobalPrefs", MODE_PRIVATE)

        val violationList = prefs.getStringSet(selectedOption.value, mutableSetOf())
        violationList?.add(name)
        val editor = prefs.edit()
        editor.putStringSet(selectedOption.value, violationList)
        editor.apply()

        Toast.makeText(this, selectedOption.value + " reported for " + name, Toast.LENGTH_SHORT).show();
    }

    private fun hasCameraPermission() = ContextCompat.checkSelfPermission(
        this, Manifest.permission.CAMERA
    ) == PackageManager.PERMISSION_GRANTED
}