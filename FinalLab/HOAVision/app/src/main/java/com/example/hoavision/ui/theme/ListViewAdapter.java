package com.example.hoavision.ui.theme;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.example.hoavision.MainActivity;
import com.example.hoavision.R;

import java.util.ArrayList;

/**
 * Custom ArrayAdapter for displaying a list of strings in a ListView.
 * Each row contains a numbered item, the item name, and icons for actions.
 */
public class ListViewAdapter extends ArrayAdapter<String> {
    ArrayList<String> list;
    Context context;

    /**
     * Constructor for the ListViewAdapter.
     *
     * @param context The current context used for inflating the layout.
     * @param items The ArrayList of strings to be displayed in the ListView.
     */
    public ListViewAdapter(Context context, ArrayList<String> items){
        super(context, R.layout.list_row, items);
        this.context = context;
        list = items;
    }

    /**
     * Creates and populates a View for each item in the ArrayList.
     *
     * @param position The position of the item in the list.
     * @param convertView The recycled view to populate, or null if a new view needs to be created.
     * @param parent The parent ViewGroup that this view will eventually be attached to.
     * @return The populated View for the item at the specified position.
     */
    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if(convertView == null){
            LayoutInflater layoutInflater = (LayoutInflater) context.getSystemService(MainActivity.LAYOUT_INFLATER_SERVICE);
            convertView = layoutInflater.inflate(R.layout.list_row, null);

            TextView number = convertView.findViewById(R.id.number);
            number.setText(position + 1 + ".");

            TextView name = convertView.findViewById(R.id.name);
            name.setText(list.get(position));


            ImageView map = convertView.findViewById(R.id.map); // added map button next to remove and weather button

        }
        return convertView;
    }
}

